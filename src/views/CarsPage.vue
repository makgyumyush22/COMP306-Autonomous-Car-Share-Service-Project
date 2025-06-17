<template>
  <div>
    <label>
      Enter User ID:
      <input type="number" v-model.number="userId" />
    </label>

    <!-- Lat/Lon Inputs -->
    <div class="latlon-inputs">
      <label>
        Latitude:
        <input type="number" step="any" v-model.number="lat" />
      </label>
      <label>
        Longitude:
        <input type="number" step="any" v-model.number="lon" />
      </label>
    </div>

    <!-- Radio Filters -->
    <div class="filters">
      <label>
        <input type="radio" value="distance" v-model="selectedFilter" />
        By distance
      </label>

      <label>
        <input type="radio" value="city" v-model="selectedFilter" />
        In city:
        <input type="text" v-model="city" :disabled="selectedFilter !== 'city'" />
      </label>

      <label>
        <input type="radio" value="price" v-model="selectedFilter" />
        By price:
        <input type="number" v-model.number="minPrice" placeholder="Min" :disabled="selectedFilter !== 'price'" />
        <input type="number" v-model.number="maxPrice" placeholder="Max" :disabled="selectedFilter !== 'price'" />
      </label>

      <label>
        <input type="radio" value="capacity" v-model="selectedFilter" />
        By capacity:
        <input type="number" v-model.number="capacity" :disabled="selectedFilter !== 'capacity'" />
      </label>
    </div>


    <div v-if="error" style="color: red">{{ error }}</div>
    <table v-else class="data-table">
      <thead>
        <tr>
          <th>Model</th>
          <th>Capacity</th>
          <th>Battery Level %</th>
          <th>Price Rate ($/km)</th>
          <th>Location</th>
          <th>Distance (km)</th>
          <th>Photo</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="car in cars" :key="car.car_id">
          <td>{{ car.model }}</td>
          <td>{{ car.capacity }}</td>
          <td>{{ car.battery_level }}</td>
          <td>{{ car.price_rate }}</td>
          <td>{{ car.city_name + ', ' + car.location_name }}</td>
          <td>{{ car.distance_km.toFixed(2) }}</td>
          <td><img :src="car.photo_URL" alt="Car photo" class="car-photo" /></td>
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
import { defineComponent, ref, onMounted, watch } from 'vue'

interface Car {
  car_id: number
  model: string
  capacity: number
  battery_level: number
  price_rate: number
  photo_URL: string
  distance_km: number
  city_name: string
  location_name: string
}

export default defineComponent({
  setup() {
    const cars = ref<Car[]>([])
    const error = ref<string | null>(null)
    const message = ref<string | null>(null)

    const selectedFilter = ref<'distance' | 'city' | 'price' | 'capacity'>('distance')
    const city = ref('')
    const minPrice = ref<number | null>(null)
    const maxPrice = ref<number | null>(null)
    const capacity = ref<number | null>(null)
    const userId = ref<number | null>(null)
    const lat = ref(41)
    const lon = ref(29)

    const fetchCars = async () => {
      let url = ''
      const params: Record<string, string> = { lat: lat.value.toString(), lon: lon.value.toString() }

      if (selectedFilter.value === 'distance') {
        url = 'http://127.0.0.1:5000/available_cars'
      } else if (selectedFilter.value === 'city') {
        url = 'http://127.0.0.1:5000/available_cars/city_distance'
        params.city = city.value.toLowerCase()
      } else if (selectedFilter.value === 'price') {
        url = 'http://127.0.0.1:5000/available_cars/price_distance'
        if (minPrice.value !== null) params.min_price = minPrice.value.toString()
        if (maxPrice.value !== null) params.max_price = maxPrice.value.toString()
      } else if (selectedFilter.value === 'capacity') {
        url = 'http://127.0.0.1:5000/available_cars/capacity_distance'
        if (capacity.value !== null) params.capacity = capacity.value.toString()
      }

      const query = new URLSearchParams(params).toString()
      try {
        const res = await fetch(`${url}?${query}`)
        if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`)
        cars.value = await res.json()
        error.value = null
      } catch (e) {
        error.value = 'Failed to load cars.'
      }
    }

    onMounted(fetchCars)
    watch([selectedFilter, city, minPrice, maxPrice, capacity, lat, lon], fetchCars)

    const reserveCar = async (car: Car) => {
      try {
        if(userId.value === null) throw new Error('No User ID set')

        const payload = {
        user_id: userId.value,
        car_id: car.car_id,
        start_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
        end_time: new Date(new Date().getTime() + 10*60000).toISOString().slice(0, 19).replace('T', ' '),
        pickup_location_id: 0,
        dropoff_location_id: 1,
        trip_cost: 12.34,
        method_id: 0
      }

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

    return {
      cars,
      error,
      message,
      reserveCar,
      formatDate,
      selectedFilter,
      city,
      minPrice,
      maxPrice,
      capacity,
      lat,
      lon,
      userId
    }
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
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  align-items: center;
}
.filters label {
  display: flex;
  align-items: center;
  gap: 5px;
}
.filters input[type="text"],
.filters input[type="number"] {
  padding: 4px;
  width: 80px;
}
.car-photo {
  max-width: 300px;
  height: auto;
  border-radius: 4px;
}
</style>
