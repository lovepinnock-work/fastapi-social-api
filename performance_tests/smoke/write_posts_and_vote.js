import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = "http://host.docker.internal:8000";

export const options = {
    vus: 1,
    iterations: 10,
    thresholds: { http_req_failed: ["rate<0.02"] },
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
    return { token };
}

export default function (data) {
    const authJson = {
      headers: { Authorization: `Bearer ${data.token}`, "Content-Type": "application/json" },
    };

    const postRes = http.post(
      `${BASE_URL}/posts/`,
      JSON.stringify({ title: `k6 smoke ${__ITER}`, content: "smoke", published: true }),
      authJson
    );
    check(postRes, { "post 201": (r) => r.status === 201 });

    const postId = postRes.json("id");

    const voteRes = http.post(
      `${BASE_URL}/vote/`,
      JSON.stringify({ post_id: postId, vote_dir: 1 }),
      authJson
    );
    check(voteRes, { "vote 201": (r) => r.status === 201 });

    const unvoteRes = http.post(
      `${BASE_URL}/vote/`,
      JSON.stringify({ post_id: postId, vote_dir: 0 }),
      authJson
    );
    check(unvoteRes, { "unvote 201": (r) => r.status === 201 || r.status === 404 });

    sleep(0.2);
}
