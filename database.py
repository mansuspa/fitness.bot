import json

class Database:
    def __init__(self):
        self.file = "db.json"
        self.data = self.load()

    def load(self):
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except:
            return {}

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=2)

    def add_user(self, uid, username):
        uid = str(uid)
        if uid not in self.data:
            self.data[uid] = {"username": username, "goal": "maintain"}
            self.save()

    def get_user(self, uid):
        return self.data.get(str(uid), {"goal": "maintain"})

    def update_user(self, uid, **kwargs):
        uid = str(uid)
        if uid in self.data:
            self.data[uid].update(kwargs)
            self.save()