import { useEffect, useMemo, useState } from "react";
import axios from "axios";

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const CITY_COORDINATES = {
  Delhi: [28.6139, 77.209],
  Mumbai: [19.076, 72.8777],
  Bangalore: [12.9716, 77.5946],
  Chennai: [13.0827, 80.2707],
  Hyderabad: [17.385, 78.4867],
  Kolkata: [22.5726, 88.3639],
  Pune: [18.5204, 73.8567],
  Ahmedabad: [23.0225, 72.5714],
};

function App() {
  const [transactions, setTransactions] = useState([]);
  const [selectedTransaction, setSelectedTransaction] = useState(null);

  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  const [analystActions, setAnalystActions] = useState({});
  const [auditLogs, setAuditLogs] = useState([]);

  const [performance, setPerformance] = useState(null);
  const [drift, setDrift] = useState(null);

  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("fraud_user");

    try {
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });

  const [loginForm, setLoginForm] = useState({
    username: "analyst",
    password: "analyst123",
  });

  const [loginError, setLoginError] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);

  const token = localStorage.getItem("fraud_access_token");

  const authConfig = () => ({
    headers: {
      Authorization: `Bearer ${localStorage.getItem(
        "fraud_access_token"
      )}`,
    },
  });

const loginAnalyst = async (event) => {
  event.preventDefault();

  setLoginLoading(true);
  setLoginError("");

  try {
    const formData = new URLSearchParams();

    formData.append("username", loginForm.username.trim());
    formData.append("password", loginForm.password);

    const response = await axios.post(
      `${API_URL}/auth/login`,
      formData,
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );

    console.log("LOGIN RESPONSE:", response.data);

    const accessToken = response.data.access_token;

    if (!accessToken) {
      throw new Error("Backend did not return an access token.");
    }

    localStorage.setItem("fraud_access_token", accessToken);
    localStorage.setItem(
      "fraud_user",
      JSON.stringify(response.data)
    );

    setUser(response.data);
  } catch (error) {
    console.error("LOGIN ERROR:", error);
    console.error("SERVER RESPONSE:", error.response?.data);

    setLoginError(
      error.response?.data?.detail ||
        error.message ||
        "Login failed. Check your username and password."
    );
  } finally {
    setLoginLoading(false);
  }
};
  const logout = () => {
    localStorage.removeItem("fraud_access_token");
    localStorage.removeItem("fraud_user");

    setUser(null);
    setTransactions([]);
    setSelectedTransaction(null);
  };

 const fetchTransactions = async () => {
  try {
    const response = await axios.get(`${API_URL}/transactions/`);

    console.log("Transactions API response:", response.data);

    setTransactions(response.data);
    setLastUpdated(new Date());

    setSelectedTransaction((current) => {
      if (!current) {
        return response.data[0] || null;
      }

      return (
        response.data.find(
          (transaction) => transaction.id === current.id
        ) || current
      );
    });
  } catch (error) {
    console.error("Backend connection error:", error);
    console.error("Error response:", error.response?.data);
  } finally {
    setLoading(false);
  }
};

  const fetchAuditLogs = async () => {
    if (!localStorage.getItem("fraud_access_token")) return;

    try {
      const response = await axios.get(
        `${API_URL}/analysts/audit-logs`,
        authConfig()
      );

      setAuditLogs(response.data);
    } catch (error) {
      console.error("Audit log error:", error);
    }
  };

  const fetchPerformance = async () => {
    if (!localStorage.getItem("fraud_access_token")) return;

    try {
      const response = await axios.get(
        `${API_URL}/analytics/model-performance`,
        authConfig()
      );

      setPerformance(response.data);
    } catch (error) {
      console.error("Performance API error:", error);
    }
  };

  const fetchDrift = async () => {
    if (!localStorage.getItem("fraud_access_token")) return;

    try {
      const response = await axios.get(
        `${API_URL}/monitoring/drift`,
        authConfig()
      );

      setDrift(response.data);
    } catch (error) {
      console.error("Drift API error:", error);
    }
  };

  const refreshAll = async () => {
    await fetchTransactions();

    if (localStorage.getItem("fraud_access_token")) {
      await Promise.all([
        fetchAuditLogs(),
        fetchPerformance(),
        fetchDrift(),
      ]);
    }
  };

  useEffect(() => {
    refreshAll();

    const interval = setInterval(refreshAll, 5000);

    return () => clearInterval(interval);
  }, [user]);

  const handleAnalystAction = async (transactionId, action) => {
    const reason = window.prompt(
      `Enter the reason for ${action.toLowerCase()}:`
    );

    if (reason === null) return;

    try {
      await axios.post(
        `${API_URL}/analysts/transactions/${transactionId}/decision`,
        {
          decision: action,
          reason: reason || "No reason provided",
        },
        authConfig()
      );

      setAnalystActions((previous) => ({
        ...previous,
        [transactionId]: action,
      }));

      await refreshAll();

      alert(`Transaction ${action.toLowerCase()}d successfully.`);
    } catch (error) {
      console.error("Analyst decision error:", error);

      if (error.response?.status === 401) {
        logout();
      }

      alert(
        error.response?.data?.detail ||
          "Unable to record analyst decision."
      );
    }
  };

  const totalTransactions = transactions.length;

  const fraudTransactions = transactions.filter(
    (transaction) => transaction.is_fraud
  ).length;

  const highRiskTransactions = transactions.filter(
    (transaction) => transaction.risk_level === "HIGH"
  ).length;

  const mediumRiskTransactions = transactions.filter(
    (transaction) => transaction.risk_level === "MEDIUM"
  ).length;

  const lowRiskTransactions = transactions.filter(
    (transaction) => transaction.risk_level === "LOW"
  ).length;

  const totalAmount = transactions.reduce(
    (sum, transaction) => sum + Number(transaction.amount || 0),
    0
  );

  const fraudRate =
    totalTransactions > 0
      ? ((fraudTransactions / totalTransactions) * 100).toFixed(1)
      : "0.0";

  const averageRisk =
    totalTransactions > 0
      ? (
          transactions.reduce(
            (sum, transaction) =>
              sum + Number(transaction.risk_score || 0),
            0
          ) / totalTransactions
        ).toFixed(1)
      : "0.0";

  const riskChartData = [
    { name: "High", value: highRiskTransactions },
    { name: "Medium", value: mediumRiskTransactions },
    { name: "Low", value: lowRiskTransactions },
  ];

  const trendData = useMemo(() => {
    return transactions
      .slice()
      .reverse()
      .slice(-12)
      .map((transaction, index) => ({
        name: `T${index + 1}`,
        risk: Number(transaction.risk_score || 0),
      }));
  }, [transactions]);

  const recentTransactions = transactions
    .slice()
    .reverse()
    .slice(0, 12);

  if (!user || !token) {
    return (
      <div className="login-page">
        <form className="login-card" onSubmit={loginAnalyst}>
          <div className="brand-icon">🛡</div>

          <h1>FraudGuard AI</h1>

          <p>
            Fraud Intelligence & Operations Platform
          </p>

          <h2>Analyst Login</h2>

          <label>Username</label>

          <input
            type="text"
            value={loginForm.username}
            onChange={(event) =>
              setLoginForm({
                ...loginForm,
                username: event.target.value,
              })
            }
            required
          />

          <label>Password</label>

          <input
            type="password"
            value={loginForm.password}
            onChange={(event) =>
              setLoginForm({
                ...loginForm,
                password: event.target.value,
              })
            }
            required
          />

          {loginError && (
            <div className="login-error">
              {loginError}
            </div>
          )}

          <button
            className="login-button"
            type="submit"
            disabled={loginLoading}
          >
            {loginLoading ? "Signing in..." : "Sign in"}
          </button>

          <small>
            Demo accounts: analyst / analyst123
          </small>
        </form>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">🛡</div>

          <div>
            <h1>FraudGuard AI</h1>
            <p>Fraud Intelligence & Operations Platform</p>
          </div>
        </div>

        <div className="topbar-right">
          <div className="analyst-info">
            <strong>{user.full_name}</strong>
            <span>{user.role}</span>
          </div>

          <div className="live-status">
            <span className="live-dot"></span>
            LIVE MONITORING
          </div>

          <button className="refresh-btn" onClick={refreshAll}>
            ↻ Refresh
          </button>

          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard">
        <section className="welcome-section">
          <div>
            <h2>Fraud Operations Center</h2>

            <p>
              AI-powered monitoring of transactions, anomalies and
              rule-based risk signals.
            </p>
          </div>

          <div className="updated">
            Last updated:{" "}
            {lastUpdated
              ? lastUpdated.toLocaleTimeString()
              : "Waiting..."}
          </div>
        </section>

        <section className="stats-grid">
          <StatCard
            title="Total Transactions"
            value={totalTransactions.toLocaleString()}
            subtitle="Transactions monitored"
            icon="↗"
          />

          <StatCard
            title="Fraud Detected"
            value={fraudTransactions}
            subtitle={`${fraudRate}% fraud rate`}
            icon="⚠"
            danger
          />

          <StatCard
            title="High Risk"
            value={highRiskTransactions}
            subtitle="Requires investigation"
            icon="!"
            warning
          />

          <StatCard
            title="Transaction Volume"
            value={`₹${totalAmount.toLocaleString("en-IN", {
              maximumFractionDigits: 0,
            })}`}
            subtitle={`Average risk ${averageRisk}/100`}
            icon="₹"
          />
        </section>

        <section className="operations-summary">
          <div className="operation-card">
            <span>Feedback Records</span>
            <strong>
              {performance?.feedback_count ?? 0}
            </strong>
          </div>

          <div className="operation-card">
            <span>Model Accuracy</span>
            <strong>
              {performance
                ? `${performance.accuracy}%`
                : "—"}
            </strong>
          </div>

          <div className="operation-card">
            <span>Drift Status</span>
            <strong className={drift?.status?.toLowerCase()}>
              {drift?.status || "Checking"}
            </strong>
          </div>

          <div className="operation-card">
            <span>Retraining</span>
            <strong>
              {drift?.retraining_required ? "Required" : "Not required"}
            </strong>
          </div>
        </section>

        <section className="main-grid">
          <div className="panel chart-panel">
            <div className="panel-title">
              <div>
                <h3>Risk Distribution</h3>
                <span>Current transaction risk levels</span>
              </div>
            </div>

            <div className="chart-container">
              {totalTransactions === 0 ? (
                <EmptyState text="No transaction data available" />
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={65}
                      outerRadius={105}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      <Cell fill="#ef4444" />
                      <Cell fill="#f59e0b" />
                      <Cell fill="#22c55e" />
                    </Pie>

                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className="panel chart-panel">
            <div className="panel-title">
              <div>
                <h3>Risk Score Trend</h3>
                <span>Recent transaction risk movement</span>
              </div>
            </div>

            <div className="chart-container">
              {trendData.length === 0 ? (
                <EmptyState text="Waiting for transactions..." />
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trendData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#e5e7eb"
                    />

                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />

                    <Line
                      type="monotone"
                      dataKey="risk"
                      stroke="#6366f1"
                      strokeWidth={3}
                      dot={{ r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel transactions-panel">
            <div className="panel-title">
              <div>
                <h3>Live Transaction Feed</h3>
                <span>
                  Automatically refreshed every 5 seconds
                </span>
              </div>

              <div className="transaction-count">
                {totalTransactions} records
              </div>
            </div>

            {loading ? (
              <div className="loading">
                Loading transaction intelligence...
              </div>
            ) : recentTransactions.length === 0 ? (
              <EmptyState text="No transactions found. Send a transaction through the API." />
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Transaction</th>
                      <th>Amount</th>
                      <th>Location</th>
                      <th>ML</th>
                      <th>Anomaly</th>
                      <th>Rules</th>
                      <th>Risk</th>
                      <th>Status</th>
                    </tr>
                  </thead>

                  <tbody>
                    {recentTransactions.map((transaction) => (
                      <tr
                        key={transaction.id}
                        className={
                          selectedTransaction?.id === transaction.id
                            ? "selected-row"
                            : ""
                        }
                        onClick={() =>
                          setSelectedTransaction(transaction)
                        }
                      >
                        <td>
                          <strong>
                            {transaction.transaction_id}
                          </strong>

                          <small>{transaction.user_id}</small>
                        </td>

                        <td>
                          ₹
                          {Number(
                            transaction.amount || 0
                          ).toLocaleString("en-IN")}
                        </td>

                        <td>{transaction.location}</td>

                        <td>
                          {Number(
                            transaction.ml_score || 0
                          ).toFixed(1)}
                        </td>

                        <td>
                          {Number(
                            transaction.anomaly_score || 0
                          ).toFixed(1)}
                        </td>

                        <td>
                          {Number(
                            transaction.rule_score || 0
                          ).toFixed(1)}
                        </td>

                        <td>
                          <strong>
                            {Number(
                              transaction.risk_score || 0
                            ).toFixed(1)}
                          </strong>
                        </td>

                        <td>
                          <RiskBadge
                            level={transaction.risk_level}
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <InvestigationPanel
            transaction={selectedTransaction}
            analystAction={
              selectedTransaction
                ? analystActions[selectedTransaction.transaction_id]
                : null
            }
            onAction={handleAnalystAction}
          />
        </section>

        <section className="panel map-panel">
          <div className="panel-title">
            <div>
              <h3>Transaction Intelligence Map</h3>
              <span>
                Geographic distribution of monitored transactions
              </span>
            </div>
          </div>

          <div className="map-wrapper">
            <MapContainer
              center={[22.9734, 78.6569]}
              zoom={5}
              scrollWheelZoom={true}
              className="fraud-map"
            >
              <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {transactions.map((transaction) => {
                const coordinates =
                  CITY_COORDINATES[transaction.location];

                if (!coordinates) return null;

                let radius = 7;

                if (transaction.risk_level === "HIGH") {
                  radius = 12;
                } else if (transaction.risk_level === "MEDIUM") {
                  radius = 9;
                }

                return (
                  <CircleMarker
                    key={`map-${transaction.id}`}
                    center={coordinates}
                    radius={radius}
                    pathOptions={{
                      color:
                        transaction.risk_level === "HIGH"
                          ? "#ef4444"
                          : transaction.risk_level === "MEDIUM"
                          ? "#f59e0b"
                          : "#22c55e",
                      fillOpacity: 0.7,
                    }}
                  >
                    <Popup>
                      <strong>
                        {transaction.transaction_id}
                      </strong>

                      <br />

                      Location: {transaction.location}

                      <br />

                      Risk:{" "}
                      {Number(
                        transaction.risk_score || 0
                      ).toFixed(1)}

                      <br />

                      Level: {transaction.risk_level}
                    </Popup>
                  </CircleMarker>
                );
              })}
            </MapContainer>
          </div>
        </section>

        <section className="panel analysis-panel">
          <div className="panel-title">
            <div>
              <h3>AI Fraud Analysis</h3>
              <span>
                Explainable signals behind the risk decision
              </span>
            </div>
          </div>

          <div className="analysis-grid">
            {recentTransactions.slice(0, 6).map((transaction) => (
              <div
                className="analysis-card"
                key={`analysis-${transaction.id}`}
              >
                <div className="analysis-header">
                  <strong>{transaction.transaction_id}</strong>

                  <RiskBadge level={transaction.risk_level} />
                </div>

                <div className="signal-bars">
                  <SignalBar
                    label="ML Model"
                    value={transaction.ml_score}
                  />

                  <SignalBar
                    label="Anomaly Detection"
                    value={transaction.anomaly_score}
                  />

                  <SignalBar
                    label="Business Rules"
                    value={transaction.rule_score}
                  />
                </div>

                <div className="reason-list">
                  {(transaction.reasons || []).length > 0 ? (
                    transaction.reasons.map((reason, index) => (
                      <div className="reason" key={index}>
                        <span>•</span>
                        {reason}
                      </div>
                    ))
                  ) : (
                    <div className="safe-message">
                      ✓ No major suspicious signals detected.
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel audit-panel">
          <div className="panel-title">
            <div>
              <h3>Recent Audit Logs</h3>
              <span>Analyst decisions recorded by the backend</span>
            </div>
          </div>

          {auditLogs.length === 0 ? (
            <EmptyState text="No analyst decisions recorded yet." />
          ) : (
            <div className="audit-list">
              {auditLogs.slice(0, 8).map((log) => (
                <div className="audit-item" key={log.id}>
                  <strong>{log.transaction_id}</strong>

                  <span>{log.decision}</span>

                  <small>
                    {log.analyst_username} —{" "}
                    {log.reason || "No reason provided"}
                  </small>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      <footer>
        <span>FraudGuard AI</span>
        <span>AI Fraud Detection & Operations Platform</span>
        <span>System Status: Operational</span>
      </footer>
    </div>
  );
}

function StatCard({
  title,
  value,
  subtitle,
  icon,
  danger,
  warning,
}) {
  return (
    <div className="stat-card">
      <div
        className={`stat-icon ${
          danger ? "danger-icon" : ""
        } ${warning ? "warning-icon" : ""}`}
      >
        {icon}
      </div>

      <div>
        <p>{title}</p>
        <h2>{value}</h2>
        <span>{subtitle}</span>
      </div>
    </div>
  );
}

function RiskBadge({ level }) {
  const safeLevel = level || "LOW";

  return (
    <span className={`risk-badge ${safeLevel.toLowerCase()}`}>
      {safeLevel}
    </span>
  );
}

function SignalBar({ label, value }) {
  const numericValue = Number(value || 0);

  return (
    <div className="signal">
      <div className="signal-label">
        <span>{label}</span>
        <strong>{numericValue.toFixed(1)}</strong>
      </div>

      <div className="signal-track">
        <div
          className="signal-fill"
          style={{
            width: `${Math.min(numericValue, 100)}%`,
          }}
        ></div>
      </div>
    </div>
  );
}

function InvestigationPanel({
  transaction,
  analystAction,
  onAction,
}) {
  if (!transaction) {
    return (
      <div className="panel investigation-panel">
        <div className="empty-investigation">
          <div className="empty-icon">🔍</div>

          <h3>Transaction Investigation</h3>

          <p>
            Select a transaction from the live feed to investigate it.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel investigation-panel">
      <div className="panel-title">
        <div>
          <h3>Investigation</h3>
          <span>{transaction.transaction_id}</span>
        </div>

        <RiskBadge level={transaction.risk_level} />
      </div>

      <div className="risk-score-large">
        <div>
          <span>Final Risk Score</span>

          <strong>
            {Number(transaction.risk_score || 0).toFixed(1)}
          </strong>
        </div>

        <div className="score-circle">
          {Number(transaction.risk_score || 0).toFixed(0)}
        </div>
      </div>

      <div className="investigation-details">
        <Detail label="User" value={transaction.user_id} />

        <Detail
          label="Amount"
          value={`₹${Number(
            transaction.amount || 0
          ).toLocaleString("en-IN")}`}
        />

        <Detail label="Merchant" value={transaction.merchant} />

        <Detail label="Location" value={transaction.location} />

        <Detail label="Device" value={transaction.device_id} />

        <Detail
          label="New Device"
          value={transaction.is_new_device ? "Yes" : "No"}
        />

        <Detail
          label="Distance"
          value={`${transaction.distance_from_previous || 0} km`}
        />

        <Detail
          label="Night Transaction"
          value={transaction.is_night ? "Yes" : "No"}
        />
      </div>

      <div className="investigation-section">
        <h4>Decision Signals</h4>

        <SignalBar
          label="Supervised ML"
          value={transaction.ml_score}
        />

        <SignalBar
          label="Anomaly Detection"
          value={transaction.anomaly_score}
        />

        <SignalBar
          label="Business Rules"
          value={transaction.rule_score}
        />
      </div>

      <div className="investigation-section">
        <h4>Why was this flagged?</h4>

        {(transaction.reasons || []).length > 0 ? (
          transaction.reasons.map((reason, index) => (
            <div className="investigation-reason" key={index}>
              <span>!</span>
              {reason}
            </div>
          ))
        ) : (
          <p className="no-reasons">
            No significant suspicious signals.
          </p>
        )}
      </div>

      <div className="analyst-section">
        <h4>Analyst Decision</h4>

        {analystAction ? (
          <div className="analyst-completed">
            ✓ Marked as <strong>{analystAction}</strong>
          </div>
        ) : (
          <div className="analyst-buttons">
            <button
              className="approve-btn"
              onClick={() =>
                onAction(
                  transaction.transaction_id,
                  "APPROVE"
                )
              }
            >
              ✓ Approve
            </button>

            <button
              className="reject-btn"
              onClick={() =>
                onAction(
                  transaction.transaction_id,
                  "REJECT"
                )
              }
            >
              ✕ Reject
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function Detail({ label, value }) {
  return (
    <div className="detail">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

function EmptyState({ text }) {
  return (
    <div className="empty-state">
      <div>📊</div>
      <p>{text}</p>
    </div>
  );
}

export default App;