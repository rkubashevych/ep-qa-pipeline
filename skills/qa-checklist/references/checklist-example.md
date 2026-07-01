# Example of a reference checklist

This example shows the quality and level of detail expected from a
checklist. Use it as a model for calibration.

## Input requirements (example)

- REQ-1: State filter — a select for filtering by state
- REQ-2: City filter — a select for filtering by city
- REQ-2a: Search by city inside the City select
- REQ-2b: Filtering the list of cities by the selected state
- REQ-2c: Show the state id next to the city name
- REQ-2d: The `order.lead.city_details` field — search by city uses
  city_details, an array of ids separated by comma

## Checklist (example)

### REQ-1: State filter — a select for filtering by state
- [ ] REQ-1.1: The State filter is present on the page
- [ ] REQ-1.2: The State filter is a select (dropdown)
- [ ] REQ-1.3: The list of states is populated with options
- [ ] REQ-1.4: The default state is nothing selected
- [ ] REQ-1.5: Selecting a state filters the results
- [ ] REQ-1.6: Clearing the state selection removes the filtering

### REQ-2: City filter — a select for filtering by city
- [ ] REQ-2.1: The City filter is present on the page
- [ ] REQ-2.2: The City filter is a select (dropdown)
- [ ] REQ-2.3: The list of cities is populated with options
- [ ] REQ-2.4: The default state is nothing selected
- [ ] REQ-2.5: Selecting a city filters the results
- [ ] REQ-2.6: Clearing the city selection removes the filtering

### REQ-2a: Search by city inside the City select
- [ ] REQ-2a.1: A search field is present inside the City select
- [ ] REQ-2a.2: Typing text filters the list of cities
- [ ] REQ-2a.3: Search works on a partial match
- [ ] REQ-2a.4: Search is case-insensitive
- [ ] REQ-2a.5: When there is no match — an empty state (no results)
- [ ] REQ-2a.6: Clearing the search returns the full list of cities

### REQ-2b: Filtering the list of cities by the selected state
- [ ] REQ-2b.1: When a state is selected, the city list shows only
  cities of that state
- [ ] REQ-2b.2: When the state is cleared, the city list shows all cities
- [ ] REQ-2b.3: When the state changes, the previous city selection is reset
- [ ] REQ-2b.4: Search inside City works within the cities filtered
  by state

### REQ-2c: Show the state id next to the city name
- [ ] REQ-2c.1: Each city option in the list displays the state id
  next to the city name
- [ ] REQ-2c.2: The state id is displayed in the selected value
  in the closed select

### REQ-2d: The order.lead.city_details field — array of ids
- [ ] REQ-2d.1: Selecting a city writes the value into
  `order.lead.city_details`
- [ ] REQ-2d.2: The value is stored as an array of ids separated by comma
- [ ] REQ-2d.3: Selecting several cities forms a correct string of
  ids separated by comma
- [ ] REQ-2d.4: Clearing the selection clears `city_details`
