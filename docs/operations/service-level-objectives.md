# Initial Service Objectives

These are 30-day operational targets, not measured production guarantees. Fleet calculation requires external aggregation because Phase 10 metrics reset per process and do not aggregate workers.

| SLI | Initial target | Source / limitation |
| --- | --- | --- |
| Availability | 99.5% of eligible requests not 5xx while readiness is expected | `echoed_http_requests_total`; exclude operator maintenance only when recorded in advance. |
| Successful request rate | >= 99.0% non-5xx | Status-family counter; expected 4xx is not server failure. |
| Server error rate | < 1.0% 5xx, with no sustained 5-minute breach | HTTP counter and `request.unhandled_exception`. |
| Latency | 95% of ordinary API requests under 1 second | Duration histogram; route-level review is needed and Course Studio import/publish may need separate budgets after production evidence. |
| Readiness | No continuous failure over 5 minutes; >= 99.5% ready checks | Health probes and database readiness metrics. |
| Auth/rate anomalies | Investigate a 3x increase over the prior comparable hour or sustained limiter triggers | Diagnostic anomaly, not a user-performance SLO; process-local counts limit precision. |

No objective is currently reliable across multiple processes without external metric collection. There is no synthetic regional availability, queue, storage durability, or end-to-end browser SLI. Rebaseline targets after 30 days of representative production-equivalent data.
