class DroneSDKCLI:
    """Provides a command-line interface for interacting with the drone SDK."""
    
    def __init__(self):
        self.commands = {
            'help': self.show_help,
            'exit': self.exit_cli,
            # Add more commands as needed
        }
    
    def run(self):
        """Start the command-line interface."""
        print("Welcome to the Drone SDK CLI. Type 'help' for a list of commands.")
        while True:
            command = input("> ").strip()
            if command in self.commands:
                self.commands[command]()
            else:
                print(f"Unknown command: {command}. Type 'help' for a list of commands.")
    
    def show_help(self):
        """Display available commands."""
        print("Available commands:")
        for command in self.commands:
            print(f" - {command}")
    
    def exit_cli(self):
        """Exit the command-line interface."""
        print("Exiting CLI.")
        exit(0)