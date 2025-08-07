<template>
  <div class="space-y-1">
    <label
      v-if="label"
      :for="id"
      :class="cn(labelVariants({ variant, size }))"
    >
      {{ label }}
    </label>
    <input
      :id="id"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :autocomplete="autocomplete"
      :required="required"
      :class="cn(inputVariants({ variant, size }))"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <div
      v-if="hint"
      :class="cn(hintVariants({ variant }))"
    >
      {{ hint }}
    </div>
    <div
      v-if="error"
      class="mt-1 text-sm text-destructive"
    >
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '~/components/ui/utils'

const inputVariants = cva(
  'flex w-full rounded-lg border bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200',
  {
    variants: {
      variant: {
        default: 'border-gray-200 focus-visible:ring-gray-300 focus-visible:border-gray-400 bg-white hover:border-gray-300',
        supportive: 'border-gray-200 focus-visible:ring-gentle-mint/30 focus-visible:border-gentle-mint/50 bg-white hover:border-gray-300',
        celebration: 'border-gray-200 focus-visible:ring-light-coral/30 focus-visible:border-light-coral/50 bg-white hover:border-gray-300',
        outline: 'border-gray-200 bg-white hover:border-gray-300',
      },
      size: {
        default: 'h-10 px-3 py-2',
        sm: 'h-9 px-3 py-1.5 text-xs',
        lg: 'h-11 px-4 py-2.5 text-base',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

const labelVariants = cva(
  'block text-sm font-medium text-gray-700 mb-1',
  {
    variants: {
      variant: {
        default: 'text-gray-600',
        supportive: 'text-gray-600',
        celebration: 'text-gray-600',
        outline: 'text-muted-foreground',
      },
      size: {
        default: 'text-sm',
        sm: 'text-xs',
        lg: 'text-base',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

const hintVariants = cva(
  'mt-1 text-xs',
  {
    variants: {
      variant: {
        default: 'text-muted-foreground',
        supportive: 'text-gray-600',
        celebration: 'text-gray-600',
        outline: 'text-muted-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

interface InputProps extends /* @vue-ignore */ VariantProps<typeof inputVariants> {
  id?: string
  type?: string
  placeholder?: string
  disabled?: boolean
  autocomplete?: string
  required?: boolean
  modelValue?: string | number
  label?: string
  hint?: string
  error?: string
}

defineProps<InputProps>()
defineEmits<{
  'update:modelValue': [value: string | number]
}>()
</script>

<style scoped>
/* Professional styling similar to Linear */
input {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-weight: 400;
  color: rgb(51, 51, 51) !important;
  letter-spacing: -0.01em;
}

label {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-weight: 500;
  letter-spacing: -0.01em;
}

/* Soft focus effect */
input:focus-visible {
  box-shadow: 0 0 0 2px rgba(156, 163, 175, 0.1);
}

/* Custom placeholder styling - not italic */
input::placeholder {
  color: rgb(156, 163, 175);
  font-style: normal;
  opacity: 0.8;
}

/* Supportive styling for different states */
input[aria-invalid="true"] {
  border-color: hsl(var(--destructive));
  background-color: hsl(var(--destructive) / 0.05);
}

input[aria-invalid="true"]:focus-visible {
  ring-color: hsl(var(--destructive) / 0.3);
  box-shadow: 0 0 0 3px hsl(var(--destructive) / 0.15);
}
</style>
