# Multi-Prepayment Loan Strategy Calculator

An interactive, single-page web application designed to simulate home/personal loan prepayment strategies and compare ROI against market investments. Evaluate whether to prepay your loan or invest your lump sums, analyze tenure reduction vs. EMI drop strategies, and visualize cumulative interest savings in real time.

---

## 🌟 Key Features

* **Dual Strategy Comparison:**
  * **Strategy A (Reduce Tenure):** Keeps monthly EMI constant and calculates how many years/months you trim off your loan.
  * **Strategy B (Reduce EMI):** Recalculates lower monthly outflows at every prepayment event while keeping original tenure.
* **Investment ROI vs. Prepayment Verdict:** Dynamically evaluates post-tax investment growth (incorporating Capital Gains Tax & Tax Brackets) against guaranteed loan interest savings.
* **Multi-Prepayment Schedule:** Add up to 5 custom lump-sum prepayments at specific years along the loan timeline.
* **Grand Total Repayment Banner:** Live calculation of total outflow across original loan terms vs. both prepayment strategies.
* **Interactive Charting:** Powered by Chart.js for real-time visualization of post-tax net worth vs. interest savings over time.
* **Zero Dependencies / No Build Step:** Runs directly in any modern browser using plain HTML, CSS, and Vanilla JavaScript.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3 (CSS Variables, Grid, Flexbox)
* **Scripting:** Vanilla JavaScript (ES6+)
* **Visualization:** [Chart.js](https://www.chartjs.org/) (via CDN)

---

## 🚀 Getting Started

### Prerequisites
* Any modern web browser (Chrome, Edge, Firefox, Safari).
* *(Optional)* Python 3.x installed if you prefer running a local HTTP server.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/multi-prepayment-loan-strategy.git](https://github.com/your-username/multi-prepayment-loan-strategy.git)
   cd multi-prepayment-loan-strategy

   Deployed at: https://loantocapital.streamlit.app/
