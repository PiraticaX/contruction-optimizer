from classical_solver import solve_classical
from ai_solver import solve_ai
from quantum_solver import solve_quantum

def run_all(df):

    classical = solve_classical(df)
    ai = solve_ai(df)
    quantum = solve_quantum(df)

    return {
        "Classical": classical,
        "AI-Heuristic": ai,
        "Quantum Benchmark": quantum
    }