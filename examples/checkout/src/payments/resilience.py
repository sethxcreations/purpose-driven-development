"""Binds the payment provider to the constitutional circuit-breaker harness.

pdd: implements OC-RES-PSP-FAILURE stratum=workflow id=A-PSP-BREAKER
"""
from harnesses.python.circuit_breaker import CircuitBreaker

psp_breaker = CircuitBreaker(failure_threshold=0.5, min_samples=20, open_seconds=30)
