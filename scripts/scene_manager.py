class Scene:
    def __init__(self, manager):
        self.manager = manager

    def handle_events(self, events):
        """Handle input events."""
        pass

    def update(self):
        """Update game logic."""
        pass

    def render(self, screen):
        """Render the scene."""
        pass

class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.active_scene = None

    def add_scene(self, name, scene):
        """Add a scene to the manager."""
        self.scenes[name] = scene

    def set_active_scene(self, name):
        """Set the active scene by name."""
        self.active_scene = self.scenes[name]

    def handle_events(self, events):
        if self.active_scene:
            self.active_scene.handle_events(events)

    def update(self):
        if self.active_scene:
            self.active_scene.update()

    def render(self, screen):
        if self.active_scene:
            self.active_scene.render(screen)
