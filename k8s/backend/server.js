// server.js (updated for live K8s data)
const express = require("express");
const cors = require("cors");
const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");

const app = express();
const PORT = 4000;

app.use(cors());
app.use(express.json());

// ───────────────────────────────────────────────────
// POD METRICS (CPU & MEMORY)
app.get("/api/pods/metrics", (req, res) => {
  exec("kubectl top pods --no-headers", (error, stdout, stderr) => {
    if (error) return res.status(500).json({ error: stderr });

    const lines = stdout.trim().split("\n");
    const parsed = lines.map((line) => {
      const [name, cpu, memory] = line.trim().split(/\s+/);
      return { name, cpu, memory };
    });

    res.json(parsed);
  });
});

// ───────────────────────────────────────────────────
// NODE METRICS
app.get("/api/nodes/metrics", (req, res) => {
  exec("kubectl top nodes --no-headers", (error, stdout, stderr) => {
    if (error) return res.status(500).json({ error: stderr });

    const lines = stdout.trim().split("\n");
    const parsed = lines.map((line) => {
      const [name, cpu, cpuPerc, mem, memPerc] = line.trim().split(/\s+/);
      return { name, cpu, cpuPerc, mem, memPerc };
    });

    res.json(parsed);
  });
});

// ───────────────────────────────────────────────────
// DUMMY CLUSTER INFO (can be extended for real multi-cluster support)
app.get("/api/clusters", (req, res) => {
  res.json([{ name: "minikube", status: "active", region: "local" }]);
});

// ───────────────────────────────────────────────────
// POD TREND SIMULATION
app.get("/api/pods/trend", (req, res) => {
  const timestamp = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  const pods = [
    { pod: "ai-model", cpu: Math.floor(Math.random() * 300), memory: 150 },
    { pod: "nginx", cpu: Math.floor(Math.random() * 100), memory: 18 },
    { pod: "collector", cpu: Math.floor(Math.random() * 180), memory: 80 },
  ];

  const data = pods.map((p) => ({
    timestamp,
    pod: p.pod,
    cpu: p.cpu,
    memory: p.memory,
  }));

  res.json(data);
});

// ───────────────────────────────────────────────────
// REMEDIATIONS (READ & WRITE)
const dataPath = path.join(__dirname, "remediated.json");

app.get("/api/remediations", (req, res) => {
  fs.readFile(dataPath, "utf8", (err, data) => {
    if (err) return res.status(500).json({ error: "Could not read file" });

    try {
      const parsed = JSON.parse(data);
      res.json(parsed);
    } catch (e) {
      res.status(500).json({ error: "Invalid JSON" });
    }
  });
});

app.post("/api/remediations", (req, res) => {
  const newItem = req.body;

  fs.readFile(dataPath, "utf8", (err, data) => {
    const parsed = err ? [] : JSON.parse(data || "[]");
    parsed.push(newItem);

    fs.writeFile(dataPath, JSON.stringify(parsed, null, 2), (err) => {
      if (err) return res.status(500).json({ error: "Could not write file" });
      res.status(200).json({ success: true });
    });
  });
});

// ───────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`✅ Metrics API running at http://localhost:${PORT}`);
});
