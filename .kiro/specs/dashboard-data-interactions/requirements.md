# Requirements Document

## Introduction

This document specifies the requirements for implementing comprehensive data interactions for the Dashboard page of a fitness tracking application. The dashboard provides users with an overview of their training progress, weight statistics, consistency tracking, today's workout plan, and recent activity history. The system must aggregate data from workout logs, training schedules, and user profiles to present meaningful insights and enable users to start their daily workouts.

## Glossary

- **Dashboard**: The main landing page displaying user fitness statistics and workout information
- **Training_Session**: A completed workout session logged by the user
- **Workout_Plan**: A structured training program containing multiple workout templates
- **Workout_Template**: A predefined set of exercises for a specific workout (e.g., "Push A")
- **Exercise**: A specific movement from the exercise library (e.g., "Bench Press")
- **Workout_Log**: A record of exercises performed with weight and reps
- **User_Profile**: Extended user information including weight, training preferences, and schedule
- **Training_Schedule**: A weekly plan assigning workout templates to specific days
- **Personal_Record**: The maximum weight lifted for a specific exercise by a user
- **Training_Volume**: The total weight lifted calculated as weight × reps × sets
- **Heatmap_Cell**: A visual representation of workout frequency for a specific day
- **API_Endpoint**: A server route that returns JSON data for frontend consumption
- **Data_Aggregator**: A service that computes statistics from raw workout data

## Requirements

### Requirement 1: Weekly Training Progress Display

**User Story:** As a user, I want to see my weekly training progress, so that I can track how many sessions I've completed this week.

#### Acceptance Criteria

1. WHEN the dashboard loads, THE Dashboard SHALL display the count of completed training sessions for the current week
2. WHEN the dashboard loads, THE Dashboard SHALL display the total planned training sessions for the current week
3. WHEN displaying weekly progress, THE Dashboard SHALL calculate the completion percentage as (completed / planned) × 100
4. WHEN displaying weekly progress, THE Dashboard SHALL render a progress bar with width proportional to the completion percentage
5. WHEN no training sessions are planned for the week, THE Dashboard SHALL display "0 / 0 sessions" with a 0% progress bar

### Requirement 2: Average Weight Statistics Display

**User Story:** As a user, I want to see my average weight over time, so that I can monitor my body weight trends.

#### Acceptance Criteria

1. WHEN the dashboard loads, THE Dashboard SHALL calculate the user's average weight from the most recent 30 days of weight entries
2. WHEN displaying average weight, THE Dashboard SHALL show the value rounded to one decimal place with "kg" unit
3. WHEN displaying weight statistics, THE Dashboard SHALL render a mini bar chart showing the last 4 weight data points
4. WHEN the user has fewer than 4 weight entries, THE Dashboard SHALL display available data points and fill remaining bars with placeholder styling
5. WHEN the user has no weight entries, THE Dashboard SHALL display a default placeholder value

### Requirement 3: Training Heatmap Visualization

**User Story:** As a user, I want to see a year-long heatmap of my training consistency, so that I can visualize my workout patterns and identify gaps.

#### Acceptance Criteria

1. WHEN the dashboard loads, THE Dashboard SHALL generate a heatmap with 371 cells representing the last 53 weeks (371 days)
2. WHEN rendering the heatmap, THE Dashboard SHALL assign color intensity to each cell based on the number of training sessions on that day
3. WHEN a day has zero training sessions, THE Dashboard SHALL render the cell with the lightest color (level 0)
4. WHEN a day has 1 training session, THE Dashboard SHALL render the cell with light color (level 1)
5. WHEN a day has 2 training sessions, THE Dashboard SHALL render the cell with medium color (level 2)
6. WHEN a day has 3 or more training sessions, THE Dashboard SHALL render the cell with the darkest color (level 3)
7. WHEN displaying the heatmap, THE Dashboard SHALL show a legend indicating "Less" to "More" intensity

### Requirement 4: Today's Workout Display

**User Story:** As a user, I want to see today's scheduled workout with a preview of exercises, so that I can quickly start my training session.

#### Acceptance Criteria

1. WHEN the dashboard loads, THE Dashboard SHALL retrieve the workout template scheduled for the current day
2. WHEN a workout is scheduled for today, THE Dashboard SHALL display the workout name in the "Start" button
3. WHEN a workout is scheduled for today, THE Dashboard SHALL display a preview list of the first 2-3 exercises in that workout
4. WHEN no workout is scheduled for today, THE Dashboard SHALL display a message indicating "No workout scheduled"
5. WHEN the user clicks the "Start" button, THE Dashboard SHALL navigate to the workout execution page with the workout template ID

### Requirement 5: Recent Activity Table Display

**User Story:** As a user, I want to see my recent workout history with key metrics, so that I can review my past performance.

#### Acceptance Criteria

1. WHEN the dashboard loads, THE Dashboard SHALL retrieve the 10 most recent completed training sessions
2. WHEN displaying recent activity, THE Dashboard SHALL show the date of each training session
3. WHEN displaying recent activity, THE Dashboard SHALL show the workout name for each session
4. WHEN displaying recent activity, THE Dashboard SHALL calculate and display the total volume for each session
5. WHEN displaying recent activity, THE Dashboard SHALL identify and display the best personal record achieved in each session
6. WHEN displaying recent activity, THE Dashboard SHALL provide an actions menu for each entry
7. WHEN the user has no workout history, THE Dashboard SHALL display "No recent activity" message

### Requirement 6: User Profile and Weight Tracking

**User Story:** As a user, I want my weight to be tracked over time, so that the system can display accurate weight statistics.

#### Acceptance Criteria

1. THE User_Profile SHALL store the user's current weight with a timestamp
2. WHEN a user updates their weight, THE System SHALL create a new weight entry with the current date
3. THE System SHALL maintain a history of all weight entries for each user
4. WHEN calculating average weight, THE System SHALL only include entries from the last 30 days
5. THE User_Profile SHALL support weight values in kilograms with one decimal precision

### Requirement 7: Workout Plan and Schedule Management

**User Story:** As a user, I want to have a structured workout plan with scheduled training days, so that the system can show me what to train each day.

#### Acceptance Criteria

1. THE Workout_Plan SHALL contain multiple Workout_Templates
2. THE Workout_Template SHALL contain a name and a list of exercises
3. THE Training_Schedule SHALL assign Workout_Templates to specific days of the week
4. WHEN retrieving today's workout, THE System SHALL query the Training_Schedule for the current day of the week
5. THE Training_Schedule SHALL support multiple workout plans per user (e.g., beginner, intermediate, advanced)
6. WHEN a user has multiple active plans, THE System SHALL use the most recently activated plan

### Requirement 8: Training Session Logging and Aggregation

**User Story:** As a developer, I want to aggregate workout logs into training sessions, so that the system can display session-level statistics.

#### Acceptance Criteria

1. THE System SHALL group Workout_Logs by user, date, and workout template to form Training_Sessions
2. WHEN calculating total volume for a session, THE System SHALL sum (weight × reps) for all exercises in that session
3. WHEN identifying personal records, THE System SHALL find the maximum weight for each exercise within a session
4. THE System SHALL compare session personal records against the user's all-time personal records
5. WHEN a new personal record is achieved, THE System SHALL mark it with a trophy indicator

### Requirement 9: API Endpoints for Dashboard Data

**User Story:** As a frontend developer, I want RESTful API endpoints to fetch dashboard data, so that I can load data dynamically without page reloads.

#### Acceptance Criteria

1. THE System SHALL provide an API endpoint `/api/dashboard/weekly-progress/` that returns completed and planned session counts
2. THE System SHALL provide an API endpoint `/api/dashboard/weight-stats/` that returns average weight and recent weight data points
3. THE System SHALL provide an API endpoint `/api/dashboard/heatmap/` that returns workout frequency data for the last 371 days
4. THE System SHALL provide an API endpoint `/api/dashboard/todays-workout/` that returns the scheduled workout template with exercise preview
5. THE System SHALL provide an API endpoint `/api/dashboard/recent-activity/` that returns the 10 most recent training sessions with metrics
6. WHEN an API endpoint is called, THE System SHALL authenticate the user and return only their data
7. WHEN an API endpoint encounters an error, THE System SHALL return appropriate HTTP status codes and error messages

### Requirement 10: Data Persistence and Integrity

**User Story:** As a system administrator, I want workout data to be stored reliably, so that users don't lose their training history.

#### Acceptance Criteria

1. THE System SHALL store all Workout_Logs with foreign key relationships to User and Exercise
2. WHEN a user is deleted, THE System SHALL cascade delete all associated workout logs and training sessions
3. WHEN an exercise is deleted from the library, THE System SHALL prevent deletion if workout logs reference it
4. THE System SHALL enforce data integrity constraints on all database models
5. THE System SHALL use database transactions when creating related records (e.g., multiple workout logs in one session)

### Requirement 11: Frontend Dynamic Data Loading

**User Story:** As a user, I want the dashboard to load quickly and update dynamically, so that I have a smooth experience.

#### Acceptance Criteria

1. WHEN the dashboard page loads, THE Frontend SHALL make asynchronous requests to all dashboard API endpoints
2. WHEN API data is received, THE Frontend SHALL update the corresponding UI components without page reload
3. WHEN API requests are pending, THE Frontend SHALL display loading indicators for each section
4. WHEN API requests fail, THE Frontend SHALL display error messages and provide retry options
5. THE Frontend SHALL cache dashboard data for 5 minutes to reduce server load on page refreshes

### Requirement 12: Heatmap Data Serialization

**User Story:** As a developer, I want to serialize heatmap data efficiently, so that the API response is fast and the frontend can render it quickly.

#### Acceptance Criteria

1. WHEN serializing heatmap data, THE System SHALL return an array of 371 objects with date and intensity level
2. WHEN calculating intensity levels, THE System SHALL use the formula: min(workout_count, 3) to cap at level 3
3. THE System SHALL generate dates for the last 371 days starting from today and going backwards
4. WHEN a date has no workout logs, THE System SHALL include it in the response with intensity level 0
5. THE Heatmap_API SHALL return data in ascending date order (oldest to newest)
