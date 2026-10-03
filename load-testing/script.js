import http from 'k6/http';
import { check } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_failed: ['rate<0.01'],
        http_req_duration: ['p(95)<500'],
    },
};

export default function () {
    // Unique URL each request so the server actually writes to the DB
    const url = `https://example.com/page/${__VU}-${__ITER}-${Date.now()}`;

    const res = http.post(
        'https://nginx-lb-vl4m.onrender.com/shorten',
        { url }, // k6 sends objects as application/x-www-form-urlencoded
    );

    check(res, {
        'status is 200': (r) => r.status === 200,
        'has short_url': (r) => r.json('short_url') !== undefined,
    });
}