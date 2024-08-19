import jinja2
import os
from datetime import datetime

class ReportGenerator:
    @staticmethod
    def generate_html_report(results):
        template_loader = jinja2.FileSystemLoader(searchpath="./src/web/templates")
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("report_template.html")

        # Process results to get summary data
        summary = ReportGenerator.generate_summary(results)

        # Generate charts data
        charts_data = ReportGenerator.generate_charts_data(results)

        return template.render(results=results, summary=summary, charts_data=charts_data, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @staticmethod
    def generate_summary(results):
        summary = {
            "total_orgs": len(results["organizations"]),
            "total_networks": 0,
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "warning_checks": 0
        }

        for org_id, org_data in results["organizations"].items():
            if "networks" in org_data:
                summary["total_networks"] += len(org_data["networks"])
                for network_id, network_data in org_data["networks"].items():
                    for check_type in ["network_checks", "switch_checks"]:
                        if check_type in network_data:
                            for check, result in network_data[check_type].items():
                                summary["total_checks"] += 1
                                if result["status"] == "OK":
                                    summary["passed_checks"] += 1
                                elif result["status"] == "WARNING":
                                    summary["warning_checks"] += 1
                                else:
                                    summary["failed_checks"] += 1

        return summary

    @staticmethod
    def generate_charts_data(results):
        charts_data = {
            "check_results": {"OK": 0, "WARNING": 0, "CRITICAL": 0},
            "org_health": {},
            "network_types": {"wireless": 0, "switch": 0, "appliance": 0, "combined": 0}
        }

        for org_id, org_data in results["organizations"].items():
            org_health = {"total": 0, "passed": 0}
            if "networks" in org_data:
                for network_id, network_data in org_data["networks"].items():
                    # Count network types
                    if "wireless" in network_data.get("productTypes", []):
                        charts_data["network_types"]["wireless"] += 1
                    if "switch" in network_data.get("productTypes", []):
                        charts_data["network_types"]["switch"] += 1
                    if "appliance" in network_data.get("productTypes", []):
                        charts_data["network_types"]["appliance"] += 1
                    if len(network_data.get("productTypes", [])) > 1:
                        charts_data["network_types"]["combined"] += 1

                    for check_type in ["network_checks", "switch_checks"]:
                        if check_type in network_data:
                            for check, result in network_data[check_type].items():
                                org_health["total"] += 1
                                charts_data["check_results"][result["status"]] += 1
                                if result["status"] == "OK":
                                    org_health["passed"] += 1

            if org_health["total"] > 0:
                charts_data["org_health"][org_id] = (org_health["passed"] / org_health["total"]) * 100

        return charts_data