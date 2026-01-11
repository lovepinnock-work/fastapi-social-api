import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = "http://host.docker.internal:8000";

export const options = {
    stages: [
        { duration: "10s", target: 5 },
        { duration: "20s", target: 15 },
        { duration: "20s", target: 30 },
        { duration: "10s", target: 0 },
    ],
    thresholds: {
        http_req_failed: ["rate<0.02"],
    },
};

function uniqueUser() {
    const suffix = `${Date.now()}_${Math.floor(Math.random() * 1e9)}`;
    return { email: `testemail${suffix}@example.com`, password: "password123@" };
}

function createUser(user) {
    const users_url = `${BASE_URL}/users/`;
    const data = JSON.stringify(user);
    const headers = { "Content-Type": "application/json" };
    return http.post(users_url, data, {headers: headers});
}

export function setup() {
      const health_route = `${BASE_URL}/health/`;
      const health = http.get(health_route);
      check(health, { "health 200": (r) => r.status === 200 });
  
      const user = uniqueUser();
      const c = createUser(user);
      check(c, { "user created 201": (r) => r.status === 201 });
  
      return user;
}

function login(user) {
    const body =
        "username=" + encodeURIComponent(user.email) +
        "&password=" + encodeURIComponent(user.password);
    const login_url = `${BASE_URL}/login/`;
    const headers = { "Content-Type": "application/x-www-form-urlencoded" };
    return http.post(login_url, body, {headers: headers});
}

export default function (user) {
    const res = login(user);
    check(res, {
        "login returns 202": (r) => r.status === 202,
        "has access token": (r) => !!r.json("access_token"),
    });
    sleep(0.2);
}
