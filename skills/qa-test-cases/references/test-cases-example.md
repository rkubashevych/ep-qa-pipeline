# Example of test cases

This example shows the expected level of detail, the format, the
application of techniques, and the distinction from the checklist.

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

## REQ-1: The State select filters the list of leads by state

Applied techniques: Use Case, EP

### TC-REQ-1.1: Filtering by state — main scenario

**Precondition:** The leads page is open, the list contains leads
from different states, the State filter = "All States"

| # | Step | Test data | Expected result |
|---|------|-----------|-----------------|
| 1 | Select a state in the State select | California [test data] | The list of leads updates |
| 2 | Check the list of leads | — | All leads in the list have the state California |
| 3 | Check the number of results | — | The count matches the number of leads from California |

**Postcondition:** State filter = California, list filtered

### TC-REQ-1.2: Returning to the full list

**Precondition:** State filter = California [test data], list filtered

| # | Step | Test data | Expected result |
|---|------|-----------|-----------------|
| 1 | Select "All States" in the State select | All States | The list of leads updates |
| 2 | Check the list of leads | — | Leads from all states are displayed |

**Postcondition:** State filter = All States, list is full

### TC-REQ-1.3: A state with no leads — empty valid partition

**Precondition:** The leads page is open, the database has states
with no leads

| # | Step | Test data | Expected result |
|---|------|-----------|-----------------|
| 1 | Select a state with no leads | Wyoming [test data] | The list of leads is empty |
| 2 | Check the display | — | A message that no leads were found is displayed |

---

## REQ-2: The City select depends on the selected state

Applied techniques: State Transition

### TC-REQ-2.1: Activating City when a state is selected

**Precondition:** The leads page is open, State = "All States",
City is inactive

| # | Step | Test data | Expected result |
|---|------|-----------|-----------------|
| 1 | Select a state in the State select | California [test data] | The City select becomes active |
| 2 | Open the City select | — | The list contains only cities from California |
| 3 | Select a city | Los Angeles [test data] | The list of leads is filtered by California + Los Angeles |

**Postcondition:** State = California, City = Los Angeles, list
filtered by both filters

### TC-REQ-2.2: Changing the state resets the selected city

**Precondition:** State = California, City = Los Angeles [test data]

| # | Step | Test data | Expected result |
|---|------|-----------|-----------------|
| 1 | Change the state | Texas [test data] | The City select is reset |
| 2 | Check the City select | — | The City value is empty, the list of cities updated with cities from Texas |
| 3 | Check the list of leads | — | All leads from Texas are displayed, without filtering by city |

**Postcondition:** State = Texas, City = empty

### TC-REQ-2.3: Deactivating City when All States is selected

**Precondition:** State = California, City = Los Angeles [test data]

| # | Step | Test data | Expected result |
|---|------|-----------|-----------------|
| 1 | Select "All States" | All States | The City select becomes inactive |
| 2 | Check the City select | — | The value is reset, the element is not clickable |
| 3 | Check the list of leads | — | Leads from all states are displayed |

**Postcondition:** State = All States, City is inactive

---

## REQ-3: The "State" label is displayed above the State select

Applied techniques: Use Case

### TC-REQ-3.1: The State label is present and positioned above the select

**Precondition:** The leads page is open

| # | Step | Test data | Expected result |
|---|------|-----------|-----------------|
| 1 | Find the label of the State select | — | A label with the text "State" is displayed above the State select |

---

## REQ-4: The Reset Filters button resets both selects

Applied techniques: Use Case, EP

### TC-REQ-4.1: Reset with both filters active

**Precondition:** State = California, City = Los Angeles [test data],
list filtered

| # | Step | Test data | Expected result |
|---|------|-----------|-----------------|
| 1 | Click "Reset Filters" | — | The State select = "All States" |
| 2 | Check the City select | — | City is inactive, the value is reset |
| 3 | Check the list of leads | — | Leads from all states are displayed |

**Postcondition:** State = All States, City is inactive, list is full

### TC-REQ-4.2: Reset with a partial filter

**Precondition:** State = California [test data], City is not selected

| # | Step | Test data | Expected result |
|---|------|-----------|-----------------|
| 1 | Click "Reset Filters" | — | The State select = "All States" |
| 2 | Check the list of leads | — | Leads from all states are displayed |

**Postcondition:** State = All States, City is inactive, list is full

---

## Statistics

- Requirements covered: 4 (REQ-1, REQ-2, REQ-3, REQ-4)
- Requirements needing clarification: 0
- Total number of test cases: 8
