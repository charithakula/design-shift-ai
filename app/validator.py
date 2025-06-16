# def detect_technology_from_text(text: str) -> str:
#     text = text.lower()
#     tech_keywords = {
#         "pega": ["pega", "case management", "rules engine", "pega platform"],
#         "servicenow": ["servicenow", "incident management", "workflow automation", "cmdb"],
#         "power platforms": ["powerapps", "power automate", "power bi", "power platform"],
#         "sap": ["sap", "s4hana", "abap", "erp"],
#         "salesforce": ["salesforce", "crm", "apex", "force.com"],
#         "customtech": ["customtech", "custom platform", "custom solution"]
#     }

#     for tech, keywords in tech_keywords.items():
#         for kw in keywords:
#             if kw in text:
#                 return tech.capitalize()
#     return "Unknown"
