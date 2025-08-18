# Per-Acre Budgeting System

## Overview
The farm management system now uses per-acre budgeting for all farm plan steps. This means:

- **Budget Entry**: When creating a farm plan step, you enter the cost per acre in ₹
- **Total Cost Calculation**: The system automatically calculates total cost by multiplying per-acre cost by plot size
- **Activity Cost Tracking**: When daily activities are logged, the system estimates actual costs based on acres worked

## How It Works

### 1. Farm Plan Step Budgeting
- Enter budget as "₹X per acre" (e.g., ₹500 per acre for plowing)
- System calculates total budget: ₹500/acre × 10 acres = ₹5,000 total

### 2. Daily Activity Cost Estimation
- When logging daily activities, specify work done as "X acres" (e.g., "2 acres")
- System calculates estimated cost: ₹500/acre × 2 acres = ₹1,000

### 3. Budget Tracking
- Total Budget: Sum of all step budgets (per-acre × plot size)
- Actual Expenses: Tracked expenses for the farm
- Progress: Shows percentage of budget used

## Example Workflow

1. **Create Farm Plan Step**:
   - Activity: Plowing
   - Budget per Acre: ₹500
   - Plot Size: 10 acres
   - **Total Budget**: ₹5,000

2. **Log Daily Activity**:
   - Date: Today
   - Activity: Plowing
   - Work Done: "2 acres"
   - **Estimated Cost**: ₹1,000

3. **View Progress**:
   - Shows total budget vs actual expenses
   - Individual activity costs based on acres worked

## Benefits
- **Scalable**: Easy to apply same rates to different plot sizes
- **Accurate**: Costs directly tied to actual work done
- **Transparent**: Clear breakdown of per-acre vs total costs
- **Flexible**: Can track partial completion of activities