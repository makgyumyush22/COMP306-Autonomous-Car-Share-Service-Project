<template>
  <div>
    <h2>Cars</h2>
    <div v-if="error" style="color: red">{{ error }}</div>
    <table v-else class="data-table">
      <thead>
        <tr>
          <th>Model</th>
          <th>Make</th>
          <th>Year</th>
          <th>License Plate</th>
          <th>Battery Level</th>
          <th>Location ID</th>
          <th>Status</th>
          <th>Last Service Date</th>
          <th>Autonomy Rating</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="car in cars" :key="car.car_id">
          <td>{{ car.model }}</td>
          <td>{{ car.make }}</td>
          <td>{{ car.year }}</td>
          <td>{{ car.license_plate }}</td>
          <td>{{ car.current_battery_level }}</td>
          <td>{{ car.current_location_id }}</td>
          <td>{{ car.status }}</td>
          <td>{{ formatDate(car.last_service_date) }}</td>
          <td>{{ car.autonomy_rating }}</td>
          <td>
            <button @click="reserveCar(car)">Reserve</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="message" style="color: green; margin-top: 10px;">{{ message }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'

interface Car {
  car_id: number
  model: string
  make: string
  year: number
  license_plate: string
  current_battery_level: number
  current_location_id: number
  status: string
  last_service_date: string
  autonomy_rating: number
}

export default defineComponent({
  setup() {
    const cars = ref<Car[]>([])
    const error = ref<string | null>(null)
    const message = ref<string | null>(null)

    onMounted(async () => {
      try {
        const res = await fetch('http://127.0.0.1:5000/available_cars')
        if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`)
        cars.value = await res.json()
      } catch (e) {
        error.value = 'Failed to load cars.'
      }
    })

    const reserveCar = async (car: Car) => {
      const payload = {
        user_id: 12345,
        car_id: car.car_id,
        start_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
        end_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
        pickup_location_id: 1,
        dropoff_location_id: 2,
        trip_cost: 12.34,
        trip_distance_km: 56.78
      }

      try {
        const res = await fetch('http://localhost:5000/reserve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })

        if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`)
        message.value = `Car ${car.car_id} reserved successfully!`
        setTimeout(() => (message.value = null), 3000)
      } catch (e) {
        message.value = `Failed to reserve ${car.car_id}.`
        setTimeout(() => (message.value = null), 3000)
      }
    }

    const formatDate = (isoString: string): string => {
      const date = new Date(isoString)
      return date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
    }

    return { cars, error, message, reserveCar, formatDate }
  },
})
</script>

<style scoped>
h2 {
  margin-bottom: 10px;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  padding: 4px 0;
}
.data-table {
  border-collapse: collapse;
  width: 100%;
  max-width: 600px;
  margin-top: 10px;
}
.data-table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: center;
  width: auto;
}
.data-table th {
  background-color: #f9f9f9;
  font-weight: bold;
  padding: 8px;
  width: auto;
}
</style>
