"use client";

import React from "react";

const SettingsPage = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow p-4">
        <h1 className="text-2xl font-bold text-gray-800">Settings</h1>
      </header>
      <main className="p-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            Application Settings
          </h2>
          <p className="text-gray-600">
            Configure various aspects of the Koda Dashboard here.
          </p>
          {/* Add your settings components here */}
          <div className="mt-4 p-4 border rounded-md bg-gray-50">
            <p className="text-gray-500">
              More settings options will be available soon.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SettingsPage;
