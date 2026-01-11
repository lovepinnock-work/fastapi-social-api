import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = "http://host.docker.internal:8000";

export const options = {
    vus: 1,
    iterations: 10,
    thresholds: { http_req_failed: ["rate<0.01"] },
};

function uniqueUser() {
    const suffix = `${Date.now()}_${Math.floor(Math.random() * 1e9)}`;
    return { email: `k6_user_${suffix}@example.com`, password: "password123@" };
}

function login(email, password) {
    const body =
      "username=" + encodeURIComponent(email) +
      "&password=" + encodeURIComponent(password);
    const res = http.post(`${BASE_URL}/login/`, body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    check(res, { "login 202": (r) => r.status === 202 });
    return res.json("access_token");
}

export function setup() {
    const health = http.get(`${BASE_URL}/health/`);
    check(health, { "health 200": (r) => r.status === 200 });

    const user = uniqueUser();
    const createRes = http.post(`${BASE_URL}/users/`, JSON.stringify(user), {
      headers: { "Content-Type": "application/json" },
    });
    check(createRes, { "user created 201": (r) => r.status === 201 });

    const token = login(user.email, user.password);
    const authJson = {
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    };

    // seed a few posts for stable reads
    const ids = [];
    for (let i = 0; i < 5; i++) {
      const p = http.post(
        `${BASE_URL}/posts/`,
        JSON.stringify({ title: `seed ${i}`, content: "seed", published: true }),
        authJson
      );
      if (p.status === 201) ids.push(p.json("id"));
    }

    check({ n: ids.length }, { "seeded >= 1": (x) => x.n >= 1 });

    return { token, ids };
}

export default function (data) {
    const auth = { headers: { Authorization: `Bearer ${data.token}` } };

    const list = http.get(`${BASE_URL}/posts/`, auth);
    check(list, { "list 200": (r) => r.status === 200 });

    const id = data.ids[Math.floor(Math.random() * data.ids.length)];
    const one = http.get(`${BASE_URL}/posts/${id}`, auth);
    check(one, { "get 200": (r) => r.status === 200 });

    sleep(0.2);
}
