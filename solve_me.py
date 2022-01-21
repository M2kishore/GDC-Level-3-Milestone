from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        priority = args[0]
        taskString = args[1]
        # check duplication
        if priority in self.current_items.keys():
            new_priority = str(int(priority) + 1)
            temp = self.current_items[priority]
            self.current_items[priority] = taskString
            self.current_items[new_priority] = temp
            pass
        self.current_items[priority] = taskString
        self.write_current()
        print('Added task: "' + taskString + '" with priority ' + priority)

    def done(self, args):
        priority = args[0]
        # check task existance
        if priority in self.current_items:
            # check if already completed by checking completed list
            if self.current_items[priority] not in self.completed_items:
                self.completed_items.append(self.current_items[priority])
                self.current_items.pop(priority)
                self.write_completed()
                self.write_current()
                print("Marked item as done.")
            else:
                pass
        else:
            print("Error: no incomplete item with priority " + priority + " exists.")

    def delete(self, args):
        priority = args[0]
        # check task existence in completed_items
        found = False
        for completed_item in self.completed_items:
            if priority in completed_item:
                found = True
                self.completed_items.remove(completed_item)
                self.write_completed()
        if priority in self.current_items.keys():
            found = True
            self.current_items.pop(priority)
            self.write_current()

        if found:
            print("Deleted item with priority " + priority)
        else:
            print(
                "Error: item with priority "
                + priority
                + " does not exist. Nothing deleted."
            )

    def ls(self):
        for index, (priority, taskString) in enumerate(self.current_items.items()):
            index+=1
            print(str(index) + ". " + taskString + " [" + str(priority) + "]")

    def report(self):
        COMPLETED_TASKS_COUNT = len(self.completed_items)
        PENDING_TASKS_COUNT = len(self.current_items)
        # print pending
        print("Pending : " + str(PENDING_TASKS_COUNT))
        for index, (priority, taskString) in enumerate(self.current_items.items()):
            print(str(index + 1) + ". " + taskString + " [" + str(priority) + "]")
        # print completed
        print()
        print("Completed : " + str(COMPLETED_TASKS_COUNT))
        for i, completed_item in enumerate(self.completed_items):
            print(str(i + 1) + ". " + completed_item)

    def render_pending_tasks(self):
        # Complete this method to return all incomplete tasks as HTML
        content = "<ul>"
        for index, (priority, taskString) in enumerate(self.current_items.items()):
            index += 1
            content += "<li>"+str(index)+". "+ taskString + " [" + str(priority) + "]"+"</li>"
        return content + "</ul>"

    def render_completed_tasks(self):
        self.read_completed()
        # Complete this method to return all completed tasks as HTML
        content = "<ul>"
        for i, completed_item in enumerate(self.completed_items):
            content += "<li>"+completed_item+"</li>"
        return content+"</ul>"



class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
