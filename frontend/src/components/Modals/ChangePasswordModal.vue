<template>
  <Dialog
    v-model="show"
    :options="{
      title: needsInitialPassword ? __('Set your password') : __('Change Password'),
    }"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <p v-if="needsInitialPassword" class="text-p-sm text-ink-gray-6">
          {{
            __(
              'Choose a password you will use to sign in. This replaces the temporary password from your invite or signup.',
            )
          }}
        </p>
        <div v-if="!needsInitialPassword">
          <Password
            v-model="currentPassword"
            :placeholder="__('Current Password')"
            maxLength="50"
          >
            <template #prefix>
              <LockKeyhole class="size-4 text-ink-gray-4" />
            </template>
          </Password>
        </div>
        <div>
          <Password
            v-model="newPassword"
            :placeholder="__('New Password')"
            maxLength="50"
          >
            <template #prefix>
              <LockKeyhole class="size-4 text-ink-gray-4" />
            </template>
          </Password>
        </div>
        <div>
          <Password
            v-model="confirmPassword"
            :placeholder="__('Confirm Password')"
            maxLength="50"
          >
            <template #prefix>
              <LockKeyhole class="size-4 text-ink-gray-4" />
            </template>
          </Password>
        </div>
      </div>
    </template>
    <template #actions>
      <div class="flex justify-between items-center">
        <div>
          <p
            v-if="confirmPasswordMessage"
            class="text-sm text-ink-gray-5"
            :class="
              confirmPasswordMessage === __('Passwords match')
                ? 'text-ink-green-3'
                : 'text-ink-red-3'
            "
          >
            {{ confirmPasswordMessage }}
          </p>
        </div>

        <Button
          variant="solid"
          :label="__('Update')"
          :disabled="!canSubmit"
          :loading="updatePassword.loading"
          @click="updatePassword.submit()"
        />
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import LockKeyhole from '~icons/lucide/lock-keyhole'
import { Dialog, toast, createResource, Password, call } from 'frappe-ui'
import { useOnboarding } from 'frappe-ui/frappe'
import { ref, watch, computed } from 'vue'

const show = defineModel({ type: Boolean })

const { updateOnboardingStep } = useOnboarding('frappecrm')

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const confirmPasswordMessage = ref('')
const needsInitialPassword = ref(false)
const passwordStatusReady = ref(false)

watch(show, async (open) => {
  if (!open) {
    passwordStatusReady.value = false
    return
  }
  passwordStatusReady.value = false
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  confirmPasswordMessage.value = ''
  try {
    const r = await call('crm.api.user.password_setup_status')
    needsInitialPassword.value = !!(r && r.needs_initial_password)
  } catch {
    needsInitialPassword.value = false
  } finally {
    passwordStatusReady.value = true
  }
})

const canSubmit = computed(() => {
  if (!passwordStatusReady.value) {
    return false
  }
  if (
    !newPassword.value ||
    !confirmPassword.value ||
    newPassword.value !== confirmPassword.value ||
    !isStrongPassword(newPassword.value)
  ) {
    return false
  }
  if (!needsInitialPassword.value && !currentPassword.value) {
    return false
  }
  return true
})

const updatePassword = createResource({
  url: 'crm.api.user.change_password',
  makeParams() {
    const initial = needsInitialPassword.value
    const params = { new_password: newPassword.value }
    params.old_password = initial ? '' : currentPassword.value
    return params
  },
  onSuccess: () => {
    updateOnboardingStep('setup_your_password')
    toast.success(__('Password updated successfully'))
    show.value = false
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    confirmPasswordMessage.value = ''
    needsInitialPassword.value = false
  },
  onError: (err) => {
    toast.error(err.messages?.[0] || __('Failed to update password'))
  },
})

function isStrongPassword(password) {
  const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d\s]).{8,}$/
  return regex.test(password)
}

watch(
  [currentPassword, newPassword, confirmPassword, needsInitialPassword, passwordStatusReady],
  () => {
    confirmPasswordMessage.value = ''

    if (
      !needsInitialPassword.value &&
      currentPassword.value &&
      newPassword.value &&
      currentPassword.value === newPassword.value
    ) {
      confirmPasswordMessage.value = __(
        'New password cannot be the same as current password',
      )
      return
    }

    if (newPassword.value && newPassword.value.length < 8) {
      confirmPasswordMessage.value = __('Password must be at least 8 characters')
      return
    } else if (newPassword.value && !isStrongPassword(newPassword.value)) {
      confirmPasswordMessage.value = __(
        'Password must contain lowercase, uppercase, number, and symbol',
      )
      return
    }

    if (
      confirmPassword.value.length &&
      newPassword.value !== confirmPassword.value
    ) {
      confirmPasswordMessage.value = __('Passwords do not match')
    } else if (
      newPassword.value === confirmPassword.value &&
      newPassword.value.length &&
      confirmPassword.value.length
    ) {
      confirmPasswordMessage.value = __('Passwords match')
    }
  },
)
</script>
