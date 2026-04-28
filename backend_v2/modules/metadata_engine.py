import logging
import time
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend_v2.database.intelligence_cache import IntelligenceCache

logger = logging.getLogger("metadata_intelligence_engine_v1")

class MetadataIntelligenceEngine:
    """
    Production-grade Metadata Intelligence Engine (MIE) for Veridex.
    Analyzes session, network, and device metadata to compute multi-dimensional risk scores.
    """
    
    def __init__(self):
        self.version = "v1.0.0"
        # Thresholds for heuristic detection
        self.velocity_threshold = 5 # max submissions per minute per device
        self.ip_threshold = 10

    def analyze(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for metadata risk analysis.
        """
        from backend_v2.core.config import settings
        
        # 1. Feature Extraction
        features = self.extract_metadata_features(metadata)
        
        # 2. Risk Computation
        geo_risk = self.compute_geo_risk(features)
        device_risk = self.compute_device_risk(features)
        session_risk = self.compute_session_risk(features)
        ip_rep = self.compute_ip_reputation(features)
        
        # 3. Redis Offline Fallback Bias
        if features.get("redis_offline"):
            # Bias risk upwards if we have no historical context
            device_risk = max(device_risk, settings.METADATA_FALLBACK_RISK)
            ip_rep = max(ip_rep, settings.METADATA_FALLBACK_RISK)
            
        # 4. Flag Generation
        flags = self._generate_flags(features, geo_risk, device_risk, session_risk, ip_rep)
        if features.get("redis_offline"):
            flags.append("REDIS_OFFLINE_BIAS")
        
        return {
            "metadata_risk": {
                "geo_risk_score": round(geo_risk, 4),
                "device_risk_score": round(device_risk, 4),
                "session_risk_score": round(session_risk, 4),
                "ip_reputation_score": round(ip_rep, 4)
            },
            "flags": flags,
            "mie_version": self.version
        }


    def extract_metadata_features(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleans and enriches raw metadata with robust Redis fallback.
        """
        from backend_v2.core.config import settings
        now = time.time()
        device_id = input_dict.get("device_id", "unknown")
        ip_addr = input_dict.get("ip_address", "0.0.0.0")
        
        # Extract basic signals
        features = {
            "device_id": device_id,
            "ip": ip_addr,
            "user_agent": input_dict.get("user_agent", ""),
            "timezone": input_dict.get("timezone", "UTC"),
            "resolution": input_dict.get("resolution", "0x0"),
            "session_id": input_dict.get("session_id", "none"),
            "language": input_dict.get("language", "en"),
            "platform": input_dict.get("platform", "unknown"),
            "timestamp_req": input_dict.get("timestamp", now),
            "processed_at": now,
            "redis_offline": False
        }
        
        # Heuristic: VPN Detection (Simulated - in prod use a GeoIP DB)
        features["is_vpn"] = self._detect_vpn(features)
        
        # Heuristic: Browser Consistency
        features["is_headless"] = "headless" in features["user_agent"].lower()
        
        try:
            # Velocity Tracking (Redis Integrated)
            ip_stats = IntelligenceCache.track_ip(ip_addr)
            dev_stats = IntelligenceCache.track_device(device_id)
            
            features["device_velocity"] = dev_stats["count"]
            features["ip_velocity"] = ip_stats["count"]
            features["global_velocity"] = IntelligenceCache.track_velocity(input_dict.get("session_id", "anon"))
            
            # Derived Feature: Time since last seen
            features["ip_idle_time"] = now - ip_stats["last_seen"]
            features["device_idle_time"] = now - dev_stats["last_seen"]
        except Exception as e:
            logger.error(f"IntelligenceCache failure (Redis offline): {e}")
            features["redis_offline"] = True
            # Conservative Fallbacks
            features["device_velocity"] = 1
            features["ip_velocity"] = 1
            features["global_velocity"] = 1
            features["ip_idle_time"] = 3600
            features["device_idle_time"] = 3600
        
        return features

    def compute_geo_risk(self, features: Dict[str, Any]) -> float:
        """
        Detects geographical anomalies and mismatches.
        """
        risk = 0.0
        
        # Rule 1: Timezone vs Language Mismatch (Simple indicator)
        # e.g., Device in 'Asia/Kolkata' but language is 'fr-FR'
        if "Asia" in features["timezone"] and "en" not in features["language"] and "hi" not in features["language"]:
            risk += 0.2
            
        # Rule 2: VPN Usage (Geo obfuscation)
        if features["is_vpn"]:
            risk += 0.4
            
        return min(risk, 1.0)

    def compute_device_risk(self, features: Dict[str, Any]) -> float:
        """
        Analyzes hardware and browser fingerprints.
        """
        risk = 0.0
        
        # Rule 1: Headless Browsers (Bot behavior)
        if features["is_headless"]:
            risk += 0.8
            
        # Rule 2: Unusual Resolution
        if features["resolution"] == "0x0" or features["resolution"] == "undefinedxundefined":
            risk += 0.3
            
        # Rule 3: Velocity Spike (Device level)
        if features["device_velocity"] > self.velocity_threshold:
            risk += 0.6
            
        return min(risk, 1.0)

    def compute_session_risk(self, features: Dict[str, Any]) -> float:
        """
        Analyzes session-level inconsistencies.
        """
        risk = 0.0
        
        # Rule 1: Missing Session Context
        if features["session_id"] == "none":
            risk += 0.2
            
        # Rule 2: Time Drift (Frontend vs Backend timestamp)
        try:
            req_ts = float(features.get("timestamp_req", 0))
            if req_ts > 0:
                drift = abs(features["processed_at"] - req_ts)
                if drift > 300: # > 5 mins drift
                    risk += 0.4
        except (ValueError, TypeError):
            risk += 0.1
            
        return min(risk, 1.0)

    def compute_ip_reputation(self, features: Dict[str, Any]) -> float:
        """
        Evaluates the reputation and behavior of the source IP.
        """
        risk = 0.0
        
        # Rule 1: IP Velocity (Global attack indicator)
        if features["ip_velocity"] > self.velocity_threshold * 2:
            risk += 0.7
            
        # Rule 2: VPN/Proxy (Often used for bulk attacks)
        if features["is_vpn"]:
            risk += 0.3
            
        return min(risk, 1.0)

    def _update_velocity(self, history: Dict[str, List[float]], key: str, now: float) -> int:
        """
        Updates and returns the number of attempts in the last minute for a key.
        """
        if key not in history:
            history[key] = []
        
        # Keep only last 60 seconds
        history[key] = [ts for ts in history[key] if now - ts < 60]
        history[key].append(now)
        
        return len(history[key])

    def _detect_vpn(self, features: Dict[str, Any]) -> bool:
        """
        Simulated VPN detection logic.
        In production, this would query a service like IPStack or MaxMind.
        """
        ua = features["user_agent"].lower()
        # Common signals of automation/proxies in User Agents or missing info
        if any(x in ua for x in ["curl", "python-requests", "postman", "phantomjs"]):
            return True
        return False

    def _generate_flags(self, features: Dict, geo: float, device: float, session: float, ip: float) -> List[str]:
        flags = []
        if features["is_vpn"]: flags.append("VPN_DETECTED")
        if features["is_headless"]: flags.append("HEADLESS_BROWSER")
        if features["device_velocity"] > self.velocity_threshold: flags.append("HIGH_DEVICE_VELOCITY")
        if features["ip_velocity"] > self.velocity_threshold * 2: flags.append("IP_VELOCITY_SPIKE")
        if geo > 0.5: flags.append("GEO_ANOMALY")
        if session > 0.5: flags.append("SESSION_DRIFT_DETECTED")
        return flags
