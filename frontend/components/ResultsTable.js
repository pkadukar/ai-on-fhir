import React from "react";

export default function ResultsTable({ data }) {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return <p>No patient data to display.</p>;
  }

  return (
    <div style={{ marginTop: "2rem" }}>
      <h2>Patient Table</h2>
      <table border="1" cellPadding="8" style={{ marginTop: "10px", width: "100%" }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Condition</th>
          </tr>
        </thead>
        <tbody>
          {data.map((patient, idx) => (
            <tr key={idx}>
              <td>{patient.name}</td>
              <td>{patient.age}</td>
              <td>{patient.condition}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
