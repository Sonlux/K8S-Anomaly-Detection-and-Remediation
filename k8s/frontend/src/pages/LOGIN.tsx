import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function LOGIN() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (username && password) {
      // TEMP login pass-through
      navigate("/");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-100 to-indigo-100">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md space-y-6">
        <h1 className="text-2xl font-bold text-center text-gray-800">
          Login to K8s Dashboard
        </h1>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 block w-full border px-3 py-2 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-300"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full border px-3 py-2 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-300"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
          >
            Sign In
          </button>
        </form>

        <div className="text-center text-sm text-gray-500">or</div>

        <button className="w-full bg-red-500 text-white py-2 rounded-md hover:bg-red-600 transition">
          Sign in with Google
        </button>

        <div className="text-center text-sm">
          New here?{" "}
          <a href="#" className="text-blue-600 hover:underline">
            Sign up
          </a>
        </div>
      </div>
    </div>
  );
}
