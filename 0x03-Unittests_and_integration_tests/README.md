# 0x03. Unittests and Integration Tests

## 📚 Description

This project focuses on writing **unit tests** and **integration tests** in Python using the `unittest` framework.

The main goals are to:
- Understand the difference between unit and integration tests.
- Learn how to mock external services (e.g., HTTP requests).
- Practice memoization testing.
- Parameterize tests using `parameterized`.
- Structure tests for maintainable, production-ready Python applications.

---

## 🛠️ Technologies

- Language: Python 3.7
- OS: Ubuntu 18.04 LTS
- Style: `pycodestyle` (v2.5)

---

## 📂 Project Structure

```bash
.
├── client.py              # Contains GithubOrgClient class
├── fixtures.py            # Contains test data/fixtures for integration tests
├── test_client.py         # Unit & integration tests for GithubOrgClient
├── test_utils.py          # Unit tests for utility functions
├── utils.py               # Utility functions (access_nested_map, get_json, memoize)
└── README.md              # Project documentation (this file)
