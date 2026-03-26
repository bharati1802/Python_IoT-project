import "./App.css";
import { useEffect, useState } from "react";
import { getTasks, addTask } from "./api";

function App() {
  const [tasks, setTasks] = useState([]);

  const [form, setForm] = useState({
    title: "",
    description: "",
    priority: "low",
    due_date: "",
    completed: false,
  });

  useEffect(() => {
    getTasks().then(setTasks);
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = async () => {
    const newTask = await addTask(form);
    setTasks([...tasks, newTask]);

    setForm({
      title: "",
      description: "",
      priority: "low",
      due_date: "",
      completed: false,
    });
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>My Task Manager</h1>

      <h2>Add Task</h2>

      <input
        name="title"
        placeholder="Title"
        value={form.title}
        onChange={handleChange}
      />
      <br /><br />

      <input
        name="description"
        placeholder="Description"
        value={form.description}
        onChange={handleChange}
      />
      <br /><br />

      <select name="priority" value={form.priority} onChange={handleChange}>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>
      <br /><br />

      <input
        type="date"
        name="due_date"
        value={form.due_date}
        onChange={handleChange}
      />
      <br /><br />

      <button onClick={handleAdd}>Add Task</button>

      <hr />

      <h2>Tasks List</h2>

      <ul>
        {tasks.map((t) => (
          <li key={t.id}>
            <b>{t.title}</b> - {t.description} ({t.priority})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;