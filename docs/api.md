# Sample API

**Version:** 1.0.0

A simple API for testing the documentation generator

---

## Endpoints

### Table of Contents

- [GET /users](#get-users)
- [POST /users](#post-users)
- [GET /users/{id}](#get-users-id)

---

<a id='get-users'></a>

### `GET` `/users`

**Summary:** List all users

Returns a paginated list of users

**Parameters:**

| Name | In | Required | Description |
|------|----|----------|-------------|
| `page` | query | No | Page number |
| `limit` | query | No | Number of items per page |

**Responses:**

- **200:** Successful response

---

<a id='post-users'></a>

### `POST` `/users`

**Summary:** Create a user

Adds a new user to the system

**Request Body:**

- **Content-Type:** `application/json`
- **Schema Type:** `object`

**Responses:**

- **201:** User created

---

<a id='get-users-id'></a>

### `GET` `/users/{id}`

**Summary:** Get user by ID

**Parameters:**

| Name | In | Required | Description |
|------|----|----------|-------------|
| `id` | path | Yes | User ID |

**Responses:**

- **200:** User found
- **404:** User not found

---

## Schemas

Reusable data models used throughout this API.

### User

**Type:** `object`

**Required Fields:** `id`, `name`, `email`

**Properties:**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| `id` | string | Yes | Unique identifier | `user-123` |
| `name` | string | Yes | User's full name | `John Doe` |
| `email` | string | Yes | User's email address | `john@example.com` |
| `createdAt` | string | No | When the user was created | `2026-01-15T10:30:00Z` |

---

### NewUser

**Type:** `object`

**Required Fields:** `name`, `email`

**Properties:**

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|
| `name` | string | Yes | User's full name | `Jane Smith` |
| `email` | string | Yes | User's email address | `jane@example.com` |

---
