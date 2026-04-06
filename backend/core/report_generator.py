"""
Report & DMCA Generator for SportShield AI.
Generates legally-formatted DMCA takedown notices and detection reports.
"""

import uuid
from datetime import datetime


class ReportGenerator:
    """Generate DMCA takedown requests and detection summary reports."""

    @classmethod
    def generate_dmca(
        cls,
        detection: dict,
        organization_name: str = "SportShield League",
        contact_email: str = "legal@sportshield.ai",
        additional_notes: str = "",
    ) -> dict:
        """
        Generate a DMCA takedown notice for a detected infringement.
        
        Args:
            detection: Detection dict with source_url, platform, confidence, etc.
            organization_name: Name of the rights holder
            contact_email: Contact email for the notice
            additional_notes: Additional context
            
        Returns:
            Report dict with id, content, and metadata
        """
        now = datetime.utcnow()
        report_id = str(uuid.uuid4())

        content = f"""
═══════════════════════════════════════════════════════════════
                    DMCA TAKEDOWN NOTICE
              Digital Millennium Copyright Act
                  17 U.S.C. § 512(c)(3)
═══════════════════════════════════════════════════════════════

Date: {now.strftime("%B %d, %Y")}
Reference Number: SS-DMCA-{report_id[:8].upper()}

TO: Content Service Provider / Platform Administrator
RE: Notice of Copyright Infringement

───────────────────────────────────────────────────────────────
1. IDENTIFICATION OF COPYRIGHTED WORK
───────────────────────────────────────────────────────────────

This notice is submitted on behalf of {organization_name}, 
the exclusive rights holder of the copyrighted sports media 
content described herein.

Asset Name: {detection.get("asset_name", "Protected Sports Media")}
Asset ID: {detection.get("asset_id", "N/A")}
SportShield Detection ID: {detection.get("id", "N/A")}
Digital Fingerprint Verified: ✓ Yes ({detection.get("confidence", 0)*100:.1f}% confidence)
Invisible Watermark Verified: ✓ Yes

───────────────────────────────────────────────────────────────
2. IDENTIFICATION OF INFRINGING MATERIAL
───────────────────────────────────────────────────────────────

Infringing URL: {detection.get("source_url", "N/A")}
Platform: {detection.get("platform", "N/A")}
Detection Type: {detection.get("detection_type", "N/A").replace("_", " ").title()}
First Detected: {detection.get("detected_at", "N/A")}
Geographic Origin: {detection.get("city", "")}, {detection.get("country", "")}

The above URL contains material that is identical or substantially 
similar to copyrighted content owned by {organization_name}. 
The material was identified using SportShield AI's proprietary 
perceptual hashing, neural fingerprinting, and invisible watermark 
verification technology with a confidence score of 
{detection.get("confidence", 0)*100:.1f}%.

───────────────────────────────────────────────────────────────
3. GOOD FAITH STATEMENT
───────────────────────────────────────────────────────────────

I have a good faith belief that the use of the described 
copyrighted material in the manner complained of is not 
authorized by the copyright owner, its agent, or the law.

───────────────────────────────────────────────────────────────
4. ACCURACY STATEMENT
───────────────────────────────────────────────────────────────

The information in this notice is accurate, and under penalty 
of perjury, I am authorized to act on behalf of the owner of 
an exclusive right that is allegedly infringed.

───────────────────────────────────────────────────────────────
5. CONTACT INFORMATION
───────────────────────────────────────────────────────────────

Organization: {organization_name}
Email: {contact_email}
Platform: SportShield AI — Digital Media Protection
Website: https://sportshield.ai

{f"Additional Notes: {additional_notes}" if additional_notes else ""}

───────────────────────────────────────────────────────────────
6. REQUESTED ACTION
───────────────────────────────────────────────────────────────

We hereby request that you immediately:
  ① Remove or disable access to the infringing material
  ② Preserve all associated metadata and access logs
  ③ Notify the uploader of this takedown notice
  ④ Provide confirmation of compliance to {contact_email}

Failure to comply may result in further legal action under the 
Digital Millennium Copyright Act and applicable international 
copyright treaties.

═══════════════════════════════════════════════════════════════
                     POWERED BY SPORTSHIELD AI
            Automated Digital Rights Management System
═══════════════════════════════════════════════════════════════
"""

        return {
            "id": report_id,
            "detection_id": detection.get("id", ""),
            "report_type": "dmca",
            "content": content.strip(),
            "created_at": now.isoformat() + "Z",
        }

    @classmethod
    def generate_summary_report(cls, asset: dict, detections: list, anomalies: list) -> str:
        """Generate a summary report for an asset's detection history."""
        now = datetime.utcnow()
        
        total = len(detections)
        high_conf = len([d for d in detections if d.get("confidence", 0) > 0.9])
        platforms = set(d.get("platform", "") for d in detections)
        countries = set(d.get("country", "") for d in detections)
        
        report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              SPORTSHIELD AI — DETECTION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Report Date: {now.strftime("%B %d, %Y at %H:%M UTC")}
Asset: {asset.get("name", "Unknown")}
Asset ID: {asset.get("id", "N/A")}

SUMMARY
───────
Total Detections: {total}
High Confidence (>90%): {high_conf}
Platforms Affected: {len(platforms)}
Countries Reached: {len(countries)}
Active Anomalies: {len(anomalies)}

PLATFORM BREAKDOWN
──────────────────
"""
        platform_counts = {}
        for d in detections:
            p = d.get("platform", "Unknown")
            platform_counts[p] = platform_counts.get(p, 0) + 1
        
        for platform, count in sorted(platform_counts.items(), key=lambda x: -x[1]):
            bar = "█" * min(count, 30)
            report += f"  {platform:20s} {bar} {count}\n"

        report += f"""
GEOGRAPHIC DISTRIBUTION
───────────────────────
"""
        country_counts = {}
        for d in detections:
            c = d.get("country", "Unknown")
            country_counts[c] = country_counts.get(c, 0) + 1
        
        for country, count in sorted(country_counts.items(), key=lambda x: -x[1])[:10]:
            bar = "█" * min(count, 30)
            report += f"  {country:20s} {bar} {count}\n"

        if anomalies:
            report += "\nACTIVE ANOMALIES\n────────────────\n"
            for a in anomalies:
                report += f"  ⚠ [{a.get('severity', '').upper()}] {a.get('anomaly_type', '').replace('_', ' ').title()}\n"
                report += f"    {a.get('description', '')[:100]}...\n\n"

        report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   POWERED BY SPORTSHIELD AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report.strip()
