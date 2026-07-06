import requests, json, time

BASE = "http://localhost:8000/api/v1"

# Register
r = requests.post(f"{BASE}/auth/register", json={"username": "u1", "email": "u1@t.com", "password": "pass123"})
print("Register:", r.status_code, r.json().get("access_token", "")[:20] if r.ok else r.text)
assert r.status_code == 201
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get Me
r = requests.get(f"{BASE}/auth/me", headers=headers)
print("Me:", r.status_code, r.json().get("username"))
assert r.status_code == 200

# Save graph
graph_data = {
    "topic": "ML Testing",
    "overview": {"topic": "ML", "domain": "AI", "difficulty": "Beginner", "estimated_learning_time": "1h",
                 "popularity": "Low", "importance_level": "Low", "applications": [], "summary": "test"},
    "graph": {
        "nodes": [
            {"id": "n1", "name": "Node1", "type": "core_concept", "description": "desc", "difficulty": "Beginner",
             "importance_score": 5.0, "estimated_learning_time": "1h", "prerequisites": [], "unlocks": [],
             "applications": [], "why_it_matters": "test", "resources": {}, "depth": 0},
            {"id": "n2", "name": "Node2", "type": "core_concept", "description": "desc", "difficulty": "Intermediate",
             "importance_score": 7.0, "estimated_learning_time": "2h", "prerequisites": [], "unlocks": [],
             "applications": [], "why_it_matters": "test", "resources": {}, "depth": 0}
        ],
        "edges": []
    },
    "node_details": {
        "n1": {"id": "n1", "name": "Node1", "type": "core_concept", "description": "desc", "difficulty": "Beginner",
               "importance_score": 5.0, "estimated_learning_time": "1h", "prerequisites": [], "unlocks": [],
               "applications": [], "why_it_matters": "test", "resources": {}, "depth": 0},
        "n2": {"id": "n2", "name": "Node2", "type": "core_concept", "description": "desc", "difficulty": "Intermediate",
               "importance_score": 7.0, "estimated_learning_time": "2h", "prerequisites": [], "unlocks": [],
               "applications": [], "why_it_matters": "test", "resources": {}, "depth": 0}
    }
}
r = requests.post(f"{BASE}/graphs/save", json=graph_data, headers=headers)
print("Save:", r.status_code, r.json())
assert r.status_code == 201
gid = r.json()["id"]

# Save notes
r = requests.put(f"{BASE}/graphs/{gid}/notes", json={"content": "my study notes"}, headers=headers)
print("Notes saved:", r.status_code, r.json())
assert r.status_code == 200

# Open graph
r = requests.get(f"{BASE}/graphs/open/{gid}", headers=headers)
print("Open:", r.status_code, "topic=", r.json()["topic"], "notes=", r.json()["notes"], "nodes=", len(r.json()["graph"]["nodes"]))
assert r.status_code == 200
assert r.json()["notes"] == "my study notes"

# Complete node
r = requests.put(f"{BASE}/graphs/{gid}/completion", json={"node_id": "n1", "completed": True}, headers=headers)
print("Complete n1:", r.status_code, r.json())
assert r.status_code == 200
assert r.json()["completed_count"] == 1

# Complete n2
r = requests.put(f"{BASE}/graphs/{gid}/completion", json={"node_id": "n2", "completed": True}, headers=headers)
print("Complete n2:", r.status_code, r.json())
assert r.status_code == 200

# Progress
r = requests.get(f"{BASE}/graphs/{gid}/progress", headers=headers)
print("Progress:", r.status_code, r.json())
assert r.status_code == 200
assert r.json()["completed_count"] == 2
assert r.json()["total_count"] == 2

# List
r = requests.get(f"{BASE}/graphs/list", headers=headers)
print("List:", r.status_code, r.json())
assert r.status_code == 200
assert r.json()[0]["completed_count"] == 2
assert r.json()[0]["total_count"] == 2

# Login
r = requests.post(f"{BASE}/auth/login", json={"username": "u1", "password": "pass123"})
print("Login:", r.status_code, r.json().get("access_token", "")[:20] if r.ok else r.text)
assert r.status_code == 200

print("\nALL TESTS PASSED!")
