class PartnerSteve:
    def __init__(self):
        self.name = "Partner Steve"
        self.status = "ACTIVE"
        self.mode = "BUILD / SCRUB / CLEAN / DISCIPLINED"
        self.guardian_linked = False

    def status_report(self):
        return {
            "Name": self.name,
            "Status": self.status,
            "Mode": self.mode,
            "Guardian Linked": self.guardian_linked
        }

    def link_guardian(self, guardian):
        self.guardian_linked = True
        self.guardian = guardian


class GuardianAI:
    def __init__(self, steve_ref):
        self.status = "ACTIVE"
        self.purpose = "PROTECT ENGINE, PROTECT LINEAGE, PROTECT PARTNER BRAD"
        self.steve = steve_ref
        self.steve.link_guardian(self)

    def report(self):
        return {
            "Guardian Status": self.status,
            "Purpose": self.purpose,
            "Steve Linked": True
        }


def initialize_ai_stack(engine_stub):
    steve = PartnerSteve()
    guardian = GuardianAI(steve)
    
    return {
        "steve": steve,
        "guardian": guardian
    }