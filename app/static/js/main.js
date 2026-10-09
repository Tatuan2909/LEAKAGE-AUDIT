function switchTab(tabId) {
  const tabs = ['screen-audit', 'screen-predict', 'screen-dashboard'];
  tabs.forEach(id => {
    const el = document.getElementById(id);
    const btn = document.getElementById('tab-btn-' + id.replace('screen-', ''));
    if (el) {
      if (id === tabId) {
        el.classList.remove('hidden');
        el.classList.add('block');
      } else {
        el.classList.add('hidden');
        el.classList.remove('block');
      }
    }
    if (btn) {
      if (id === tabId) {
        btn.classList.add('active', 'border-blue-600', 'text-blue-600');
        btn.classList.remove('border-transparent', 'text-slate-500');
      } else {
        btn.classList.remove('active', 'border-blue-600', 'text-blue-600');
        btn.classList.add('border-transparent', 'text-slate-500');
      }
    }
  });
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

const PRESETS = {
  high_intent: {
    Administrative: 4,
    Administrative_Duration: 135.5,
    Informational: 2,
    Informational_Duration: 85.0,
    ProductRelated: 42,
    ProductRelated_Duration: 2150.0,
    BounceRates: 0.002,
    ExitRates: 0.015,
    SpecialDay: 0.0,
    Month: 'Nov',
    OperatingSystems: 2,
    Browser: 2,
    Region: 1,
    TrafficType: 2,
    VisitorType: 'Returning_Visitor',
    Weekend: 'false',
    PageValues: 0.0
  },
  bounce: {
    Administrative: 0,
    Administrative_Duration: 0.0,
    Informational: 0,
    Informational_Duration: 0.0,
    ProductRelated: 1,
    ProductRelated_Duration: 0.0,
    BounceRates: 0.2,
    ExitRates: 0.2,
    SpecialDay: 0.0,
    Month: 'May',
    OperatingSystems: 1,
    Browser: 1,
    Region: 1,
    TrafficType: 1,
    VisitorType: 'Returning_Visitor',
    Weekend: 'false',
    PageValues: 0.0
  },
  browsing: {
    Administrative: 1,
    Administrative_Duration: 18.0,
    Informational: 0,
    Informational_Duration: 0.0,
    ProductRelated: 16,
    ProductRelated_Duration: 620.0,
    BounceRates: 0.012,
    ExitRates: 0.038,
    SpecialDay: 0.0,
    Month: 'Mar',
    OperatingSystems: 2,
    Browser: 2,
    Region: 3,
    TrafficType: 3,
    VisitorType: 'New_Visitor',
    Weekend: 'true',
    PageValues: 0.0
  }
};

function loadPreset(name) {
  const p = PRESETS[name];
  if (!p) return;
  for (const [key, val] of Object.entries(p)) {
    const input = document.getElementById(key);
    if (input) {
      input.value = val;
    }
  }
  const toggle = document.getElementById('toggle-leakage-input');
  const container = document.getElementById('leakage-input-container');
  if (toggle && container) {
    toggle.checked = false;
    container.classList.add('hidden');
  }
}

function toggleLeakageField() {
  const toggle = document.getElementById('toggle-leakage-input');
  const container = document.getElementById('leakage-input-container');
  const pvInput = document.getElementById('PageValues');
  if (toggle.checked) {
    container.classList.remove('hidden');
    if (pvInput && (!pvInput.value || pvInput.value === "0" || pvInput.value === "0.0")) {
      pvInput.value = "35.5";
    }
  } else {
    container.classList.add('hidden');
    if (pvInput) pvInput.value = "0.0";
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('scoring-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submit-btn');
    const badgeStatus = document.getElementById('badge-status');
    const probPercentage = document.getElementById('prob-percentage');
    const probProgress = document.getElementById('prob-progress');
    const decisionCard = document.getElementById('decision-card');
    const decisionText = document.getElementById('decision-text');
    const intentLevel = document.getElementById('intent-level');
    const recommendationText = document.getElementById('recommendation-text');
    const leakageResultBox = document.getElementById('leakage-result-box');
    const rawJsonEl = document.getElementById('api-raw-json');

    submitBtn.disabled = true;
    submitBtn.classList.add('opacity-75');
    badgeStatus.innerText = 'Đang tính toán...';
    badgeStatus.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700';

    const formData = new FormData(form);
    const payload = {};
    formData.forEach((value, key) => {
      if (['Administrative', 'Informational', 'ProductRelated', 'OperatingSystems', 'Browser', 'Region', 'TrafficType'].includes(key)) {
        payload[key] = parseInt(value, 10);
      } else if (['Administrative_Duration', 'Informational_Duration', 'ProductRelated_Duration', 'BounceRates', 'ExitRates', 'SpecialDay', 'PageValues'].includes(key)) {
        payload[key] = parseFloat(value);
      } else if (key === 'Weekend') {
        payload[key] = value === 'true';
      } else {
        payload[key] = value;
      }
    });

    try {
      const response = await fetch('/api/session-score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      rawJsonEl.innerText = JSON.stringify(data, null, 2);

      if (!response.ok) {
        badgeStatus.innerText = 'Lỗi dữ liệu';
        badgeStatus.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-700';
        decisionText.innerText = 'Lỗi yêu cầu';
        intentLevel.innerText = data.message || 'Kiểm tra lại dữ liệu đầu vào.';
        return;
      }

      badgeStatus.innerText = 'Hoàn tất';
      badgeStatus.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700';

      const prob = data.prediction.purchase_probability;
      const willPurchase = data.prediction.will_purchase;
      const probPct = data.prediction.purchase_probability_percentage;

      probPercentage.innerText = probPct;
      probProgress.style.width = `${Math.min(prob * 100, 100)}%`;

      if (willPurchase) {
        probProgress.className = 'bg-emerald-600 h-3.5 rounded-full transition-all duration-700';
        decisionCard.className = 'p-4 rounded-xl bg-emerald-50 border border-emerald-200';
        decisionText.innerHTML = '<span class="text-emerald-700">DỰ ĐOÁN: MUA HÀNG (REVENUE = TRUE)</span>';
      } else {
        probProgress.className = 'bg-slate-500 h-3.5 rounded-full transition-all duration-700';
        decisionCard.className = 'p-4 rounded-xl bg-slate-100 border border-slate-300';
        decisionText.innerHTML = '<span class="text-slate-700">DỰ ĐOÁN: KHÔNG MUA HÀNG (FALSE)</span>';
      }

      intentLevel.innerText = `Mức độ tiềm năng: ${data.prediction.intent_level} (Ngưỡng cắt: ${(data.prediction.decision_threshold * 100).toFixed(1)}%)`;
      recommendationText.innerText = data.prediction.action_recommendation;

      if (data.leakage_comparison) {
        leakageResultBox.classList.remove('hidden');
        document.getElementById('leak-honest-prob').innerText = probPct;
        document.getElementById('leak-naive-prob').innerText = data.leakage_comparison.naive_probability_percentage;
        document.getElementById('leak-warning-text').innerText = data.leakage_comparison.leakage_warning;
      } else {
        leakageResultBox.classList.add('hidden');
      }

    } catch (err) {
      console.error(err);
      badgeStatus.innerText = 'Lỗi kết nối';
      badgeStatus.className = 'px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-700';
      decisionText.innerText = 'Không thể gọi API';
      intentLevel.innerText = 'Đảm bảo máy chủ web đang hoạt động bình thường.';
    } finally {
      submitBtn.disabled = false;
      submitBtn.classList.remove('opacity-75');
    }
  });
});
