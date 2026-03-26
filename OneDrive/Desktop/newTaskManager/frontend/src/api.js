const API = "http://127.0.0.1:8000";

export const getTasks = async () => {
  const res = await fetch(`${API}/tasks`);
  return res.json();
};

export const addTask = async (task) => {
  const res = await fetch(`${API}/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(task),
  });
  return res.json();
};