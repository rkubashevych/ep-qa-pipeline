# Example of test cases

This example shows the expected level of detail, the format, the
application of techniques, and the distinction from the checklist.
It uses the Jira-friendly vertical block layout from
output-template.md — no wide tables.

Requirements for the example (identical to checklist-example):

- REQ-1: The State select filters the list of leads by the selected
  state. The default state is nothing selected (All States). The
  list of states is loaded from the API.
- REQ-2: The City select filters the list of leads by city. It
  depends on the selected state — when the state changes, the list
  of cities updates. When "All States" is selected, the list of
  cities is empty and the select is inactive.
- REQ-3: The "State" label is displayed above the State select.
- REQ-4: The "Reset Filters" button resets both selects and returns
  the list of leads to the full list.

---

## REQ-1 — The State select filters the list of leads by state  [UI]

Applied techniques: Use Case, EP

### TC-REQ-1.1 — Filtering by state — main scenario

Pre: leads page open; list has leads from different states;
  State filter = "All States"
Steps:
1. Select a state in the State select
   [data: California [test data]]
2. Check the list of leads
3. Check the number of results
Exp:
- The list of leads updates
- All leads in the list have the state California
- The count matches the number of leads from California
Post: State filter = California, list filtered

### TC-REQ-1.2 — Returning to the full list

Pre: State filter = California [test data], list filtered
Steps:
1. Select "All States" in the State select
2. Check the list of leads
Exp:
- The list of leads updates
- Leads from all states are displayed
Post: State filter = All States, list is full

### TC-REQ-1.3 — A state with no leads — empty valid partition

Pre: leads page open; the database has states with no leads
Steps:
1. Select a state with no leads [data: Wyoming [test data]]
2. Check the display
Exp:
- The list of leads is empty
- A message that no leads were found is displayed

---

## REQ-2 — The City select depends on the selected state  [UI]

Applied techniques: State Transition

### TC-REQ-2.1 — Activating City when a state is selected

Pre: leads page open; State = "All States"; City is inactive
Steps:
1. Select a state in the State select
   [data: California [test data]]
2. Open the City select
3. Select a city [data: Los Angeles [test data]]
Exp:
- The City select becomes active after step 1
- The City list contains only cities from California
- The list of leads is filtered by California + Los Angeles
Post: State = California, City = Los Angeles, list filtered
  by both filters

### TC-REQ-2.2 — Changing the state resets the selected city

Pre: State = California, City = Los Angeles [test data]
Steps:
1. Change the state [data: Texas [test data]]
2. Check the City select
3. Check the list of leads
Exp:
- The City select is reset
- The City value is empty; the list of cities updates with
  cities from Texas
- All leads from Texas are displayed, without filtering by city
Post: State = Texas, City = empty

### TC-REQ-2.3 — Deactivating City when All States is selected

Pre: State = California, City = Los Angeles [test data]
Steps:
1. Select "All States"
2. Check the City select
3. Check the list of leads
Exp:
- The City select becomes inactive
- The City value is reset; the element is not clickable
- Leads from all states are displayed
Post: State = All States, City is inactive

---

## REQ-3 — The "State" label is displayed above the State select  [UI]

Applied techniques: Use Case

### TC-REQ-3.1 — The State label is present above the select

Pre: leads page open
Steps:
1. Find the label of the State select
Exp:
- A label with the text "State" is displayed above the
  State select

---

## REQ-4 — The Reset Filters button resets both selects  [UI]

Applied techniques: Use Case, EP

### TC-REQ-4.1 — Reset with both filters active

Pre: State = California, City = Los Angeles [test data],
  list filtered
Steps:
1. Click "Reset Filters"
2. Check the City select
3. Check the list of leads
Exp:
- The State select = "All States"
- City is inactive, the value is reset
- Leads from all states are displayed
Post: State = All States, City is inactive, list is full

### TC-REQ-4.2 — Reset with a partial filter

Pre: State = California [test data], City is not selected
Steps:
1. Click "Reset Filters"
2. Check the list of leads
Exp:
- The State select = "All States"
- Leads from all states are displayed
Post: State = All States, City is inactive, list is full

---

## Statistics

- Requirements covered: 4 (REQ-1, REQ-2, REQ-3, REQ-4)
- Requirements needing clarification: 0
- Channel breakdown: [UI] 8 · [API] 0 · [mobile] 0 · [export/email] 0
- Total number of test cases: 8
