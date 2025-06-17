<template>
  <div>
    <h2>User Info</h2>

    <label>
      Enter User ID:
      <input type="number" v-model.number="userId" @change="loadAllUserData" />
    </label>

    <div v-if="user">
      <label>
        Enter Password:
        <input type="password" v-model="enteredPassword" />
      </label>
    </div>

    <div v-if="error" style="color: red">{{ error }}</div>

    <div v-if="user && passwordMatch">
      <h3>User Info</h3>
      <p><strong>Name:</strong> {{ user.name }}</p>
      <p><strong>Zip:</strong> {{ user.zip }}</p>

      <h3>Payment Methods</h3>
      <ul>
        <li v-for="pm in paymentMethods" :key="pm.method_id">
          {{ pm.card_type }} - {{ pm.card_number }}
        </li>
      </ul>

      <h3>Active Reservation</h3>
      <div v-if="activeReservation">
        <p><strong>Car:</strong> {{ activeReservation.car_model }}</p>
        <p><strong>Pickup:</strong> {{ activeReservation.pickup_city }} - {{ activeReservation.pickup_location }}</p>
        <p><strong>Dropoff:</strong> {{ activeReservation.dropoff_city }} - {{ activeReservation.dropoff_location }}</p>
        <p><strong>Time:</strong> {{ formatDate(activeReservation.start_time) }} to {{ formatDate(activeReservation.end_time) }}</p>
        <p><strong>Cost:</strong> ${{ activeReservation.trip_cost }}</p>
      </div>
      <div v-else>
        No active reservation.
      </div>

      <h3>Past Reservations</h3>
      <ul>
        <li v-for="res in reservations" :key="res.reservation_id">
          <p><strong>Car:</strong> {{ res.car_model }}</p>
          <p><strong>Time:</strong> {{ formatDate(res.start_time) }} to {{ formatDate(res.end_time) }}</p>
          <p><strong>From:</strong> {{ res.pickup_city }} - {{ res.pickup_location }}</p>
          <p><strong>To:</strong> {{ res.dropoff_city }} - {{ res.dropoff_location }}</p>
          <p><strong>Cost:</strong> ${{ res.trip_cost }}</p>
          <hr />
        </li>
      </ul>
    </div>
  </div>
</template>


<script lang="ts">
import { defineComponent, ref, computed } from 'vue'

export default defineComponent({
  setup() {
    const userId = ref<number | null>(null)
    const user = ref<any>(null)
    const paymentMethods = ref<any[]>([])
    const reservations = ref<any[]>([])
    const activeReservation = ref<any | null>(null)
    const error = ref<string | null>(null)
    const enteredPassword = ref<string>('')

    const passwordMatch = computed(() => {
      return user.value && enteredPassword.value === user.value.password
    })

    const loadAllUserData = async () => {
      if (userId.value === null) return

      error.value = null
      user.value = null
      enteredPassword.value = ''

      try {
        const [userRes, pmRes, pastRes, activeRes] = await Promise.all([
          await fetch(`http://127.0.0.1:5000/user/${userId.value}`),
          await fetch(`http://127.0.0.1:5000/user/${userId.value}/payment_methods`),
          await fetch(`http://127.0.0.1:5000/user/${userId.value}/reservations`),
          await fetch(`http://127.0.0.1:5000/user/${userId.value}/active_reservation`)
        ])

        if (!userRes.ok || !pmRes.ok || !pastRes.ok || !activeRes.ok) {
          throw new Error('One or more requests failed.')
        }

        user.value = await userRes.json()
        paymentMethods.value = await pmRes.json()
        reservations.value = await pastRes.json()
        activeReservation.value = await activeRes.json()
      } catch (e: any) {
        error.value = e.message || 'Failed to load user data.'
      }
    }

    const formatDate = (datetime: string): string => {
      return new Date(datetime).toLocaleString()
    }

    return {
      userId,
      user,
      paymentMethods,
      reservations,
      activeReservation,
      error,
      enteredPassword,
      passwordMatch,
      loadAllUserData,
      formatDate
    }
  }
})
</script>


<style scoped>
h2, h3 {
  margin-top: 20px;
}
input[type="number"] {
  margin: 10px;
  padding: 4px;
}
ul {
  padding-left: 20px;
}
hr {
  margin: 10px 0;
}
</style>

