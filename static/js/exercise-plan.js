/**
 * Exercise Plan Generator
 * Handles form submission to generate personalized exercise recommendations
 * via AJAX. Displays results with formatted plan details and error handling.
 */

document.getElementById('metricsForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const weight = document.getElementById('weight').value;
  const height = document.getElementById('height').value;
  const goal = document.getElementById('goal').value;
  
  // Show loading state and hide previous results
  document.getElementById('resultsSection').style.display = 'none';
  document.getElementById('errorState').style.display = 'none';
  document.getElementById('loadingState').style.display = 'flex';
  
  try {
    const response = await fetch(window.exercisePlanApiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
      },
      body: JSON.stringify({
        weight_kg: parseFloat(weight),
        height_cm: parseFloat(height),
        goal: goal,
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      displayPlan(result.data);
    } else {
      showError(result.error);
    }
  } catch (error) {
    showError('Failed to generate plan. Please try again.');
    console.error(error);
  } finally {
    document.getElementById('loadingState').style.display = 'none';
  }
});

/**
 * Display the exercise plan data formatted with HTML
 * @param {Object} data - The exercise plan data from the API
 */
function displayPlan(data) {
  const bmiValue = document.getElementById('bmiValue');
  const bmiCategory = document.getElementById('bmiCategory');
  const planResults = document.getElementById('planResults');
  
  // Display BMI calculation results
  bmiValue.textContent = data.bmi;
  bmiCategory.textContent = data.category;
  
  // Build plan HTML structure
  let planHTML = `
    <div class="plan-header">
      <h3>${data.plan.category}</h3>
      <p>Focus: ${data.plan.focus}</p>
      <p>Weekly Frequency: ${data.plan.weekly_frequency}</p>
    </div>
    
    <div class="weekly-plan">
  `;
  
  // Add each day's exercises
  data.plan.weekly_plan.forEach(day => {
    planHTML += `
      <div class="day-plan">
        <h4>${day.day}</h4>
        <p>${day.focus}</p>
        <ul class="exercises-list">
    `;
    
    day.exercises.forEach(exercise => {
      planHTML += `
        <li class="exercise-item">
          <span class="exercise-name">${exercise.name}</span>
          ${exercise.sets ? ` - ${exercise.sets} sets` : ''}
          ${exercise.reps ? ` x ${exercise.reps}` : ''}
          ${exercise.duration ? ` (${exercise.duration})` : ''}
        </li>
      `;
    });
    
    planHTML += `
        </ul>
      </div>
    `;
  });
  
  planHTML += `</div>`;
  
  // Add optional nutrition section
  if (data.plan.nutrition_focus) {
    planHTML += `
      <div class="nutrition-section">
        <h4>Nutrition Focus</h4>
        <p>${data.plan.nutrition_focus}</p>
      </div>
    `;
  }
  
  // Add important notes with special styling
  if (data.plan.important_notes) {
    planHTML += `
      <div class="nutrition-section" style="border-left-color: #FFD700; margin-top: 1rem;">
        <h4 style="color: #FFD700;">Important Notes</h4>
        <ul style="padding-left: 1rem; margin: 0;">
    `;
    data.plan.important_notes.forEach(note => {
      planHTML += `<li style="color: var(--secondary-neutral); margin-bottom: 0.5rem;">${note}</li>`;
    });
    planHTML += `</ul></div>`;
  }
  
  planResults.innerHTML = planHTML;
  document.getElementById('resultsSection').style.display = 'flex';
}

/**
 * Display an error message to the user
 * @param {string} message - The error message to display
 */
function showError(message) {
  document.getElementById('errorMessage').textContent = message;
  document.getElementById('errorState').style.display = 'block';
}
