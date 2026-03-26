import "./App.css";
import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [tasks, setTasks] = useState([]);

  const [form, setForm] = useState({
    title: "",
    description: "",
    priority: "medium",
    due_date: "",
    completed: false
  });

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    const res = await fetch("http://127.0.0.1:8000/tasks");
    const data = await res.json();
    setTasks(data);
  };

  const handleAdd = async () => {
    if (!form.title || !form.due_date) {
      alert("Title and Date required");
      return;
    }

    await fetch("http://127.0.0.1:8000/tasks", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(form)
    });

    setForm({
      title: "",
      description: "",
      priority: "medium",
      due_date: "",
      completed: false
    });

    fetchTasks();
  };

  return (
    <div className="container">
      <h1>Task Manager 🚀</h1>

      <input
        placeholder="Title"
        value={form.title}
        onChange={(e) => setForm({ ...form, title: e.target.value })}
      />

      <input
        placeholder="Description"
        value={form.description}
        onChange={(e) =>
          setForm({ ...form, description: e.target.value })
        }
      />

      <select
        value={form.priority}
        onChange={(e) =>
          setForm({ ...form, priority: e.target.value })
        }
      >
        <option>low</option>
        <option>medium</option>
        <option>high</option>
      </select>

      <input
        type="date"
        value={form.due_date}
        onChange={(e) =>
          setForm({ ...form, due_date: e.target.value })
        }
      />

      <button onClick={handleAdd}>Add Task</button>

      <h2>Tasks</h2>

      {tasks.map((t, i) => (
        <div key={i} className="task">
          <h3>{t.title}</h3>
          <p>{t.description}</p>
          <p>{t.priority}</p>
          <p>{t.due_date}</p>
        </div>
      ))}
    </div>
  );
}

export default App;