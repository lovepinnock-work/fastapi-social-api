import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = "http://host.docker.internal:8000";

export const options = {
    vus: 1,
    iterations: 5,
    thresholds: {
        http_req_failed: ["rate<0.01"],
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

function login(user) {
    const body =
        "username=" + encodeURIComponent(user.email) +
        "&password=" + encodeURIComponent(user.password);
    const login_url = `${BASE_URL}/login/`;
    const headers = { "Content-Type": "application/x-www-form-urlencoded" };
    return http.post(login_url, body, {headers: headers});
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

export default function (user) {
    const res = login(user);
    check(res, {
        "login returns 202": (r) => r.status === 202,
        "has access token": (r) => !!r.json("access_token"),
    });
    sleep(0.2);
}
