
# core/trigger_manager.py

class TriggerManager:
    def __init__(self, game_manager):
        print("DEBUG: TriggerManager __init__ started")
        self.game_manager = game_manager
        self.triggers = []
        print("DEBUG: TriggerManager __init__ completed")

    def register_trigger(self, trigger):
        """Registers a trigger dictionary with keys: 'event', 'condition', 'action'"""
        self.triggers.append(trigger)

    def check_and_trigger(self, event_type, **kwargs):
        print(f"DEBUG: Checking triggers for event: {event_type} with {kwargs}")

        # Push trigger as stack item instead of resolving instantly
        self.game_manager.stack_manager.add_to_stack(
            type='trigger',
            source_card=kwargs['card'],
            controller=kwargs['player'].name,
            targets=[],  # Targeting comes later
            metadata={
                'event': event_type,
                'trigger_info': f'{kwargs["card"].name} ETB trigger'  # Placeholder
            }
        )

    def resolve_trigger(self, stack_item):
        print(f"✨ Resolving triggered ability from {stack_item['source_card'].name}.")

# EXAMPLE USAGE:
# trigger = {
#     "event": "enters_battlefield",
#     "condition": lambda ctx: ctx['card'].name == "Tireless Provisioner",
#     "action": lambda ctx: ctx['player'].create_token("Food"),
# }
# trigger_manager.register_trigger(trigger)
