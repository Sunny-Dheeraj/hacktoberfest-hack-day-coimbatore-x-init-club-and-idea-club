"""Unit tests for JavaScript and TypeScript Analyzer."""

import pytest
from app.analyzers.javascript_analyzer import JavaScriptAnalyzer


def test_react_and_typescript_tsx_file():
    analyzer = JavaScriptAnalyzer()
    code = """import React, { useState, useEffect } from 'react';

interface UserProfileProps {
    userId: string;
    isActive: boolean;
}

export const UserCard: React.FC<UserProfileProps> = ({ userId, isActive }) => {
    const [count, setCount] = useState<number>(0);

    useEffect(() => {
        console.log("Mounted", userId);
    }, [userId]);

    return (
        <div className="card">
            <h1>User: {userId}</h1>
            <button onClick={() => setCount(count + 1)}>Increment</button>
        </div>
    );
};
"""
    result = analyzer.analyze("src/UserCard.tsx", code, repository="web-client")

    assert result.language == "typescript"
    signal_names = [s.name for s in result.signals]

    assert "import_react" in signal_names
    assert "useState" in signal_names
    assert "useEffect" in signal_names
    assert "UserProfileProps" in signal_names
    assert "UserCard" in signal_names
    assert "jsx_element" in signal_names

    ts_signals = [s for s in result.signals if s.technology == "TypeScript"]
    assert len(ts_signals) > 0


def test_express_backend_routes():
    analyzer = JavaScriptAnalyzer()
    code = """const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/api/users', async (req, res) => {
    const data = await fetch('https://api.example.com/data');
    res.json({ users: [] });
});

app.post('/api/users', (req, res) => {
    res.status(201).send();
});
"""
    result = analyzer.analyze("server.js", code, repository="express-api")

    assert result.language == "javascript"
    signal_names = [s.name for s in result.signals]

    assert "express" in signal_names
    assert "express_route_handler" in signal_names
    assert "node_builtin" in signal_names
    assert "async_await" in signal_names
    assert "fetch" in signal_names

    route_signals = [s for s in result.signals if s.name == "express_route_handler"]
    assert len(route_signals) == 2


def test_malformed_js_does_not_crash():
    analyzer = JavaScriptAnalyzer()
    malformed_code = """import { { broken syntax +++ ;;;
    function ( {
"""
    result = analyzer.analyze("broken.js", malformed_code, repository="client-app")
    assert isinstance(result.signals, list)
