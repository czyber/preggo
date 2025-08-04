<template>
  <div class="relative">
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
    <label
      v-if="label"
      :for="id"
      :class="cn(labelVariants({ variant, size }))"
    >
      {{ label }}
    </label>
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
import { cn } from '~/utils/cn'

const inputVariants = cva(
  'flex w-full rounded-xl border bg-background px-4 py-3 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200',
  {
    variants: {
      variant: {
        default: 'border-warm-beige focus-visible:ring-soft-pink/50 focus-visible:border-soft-pink bg-white',
        supportive: 'border-gentle-mint focus-visible:ring-gentle-mint/50 focus-visible:border-gentle-mint bg-gentle-mint/5',
        celebration: 'border-light-coral focus-visible:ring-light-coral/50 focus-visible:border-light-coral bg-light-coral/5',
        outline: 'border-input bg-background hover:bg-accent hover:text-accent-foreground',
      },
      size: {
        default: 'h-12 px-4 py-3',
        sm: 'h-10 px-3 py-2 text-sm',
        lg: 'h-14 px-5 py-4 text-base',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

const labelVariants = cva(
  'absolute left-4 transition-all duration-200 pointer-events-none font-primary',
  {
    variants: {
      variant: {
        default: 'text-gray-600',
        supportive: 'text-gray-600',
        celebration: 'text-gray-600',
        outline: 'text-muted-foreground',
      },
      size: {
        default: '-top-2.5 text-sm bg-background px-2',
        sm: '-top-2 text-xs bg-background px-2',
        lg: '-top-3 text-base bg-background px-2',
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
/* Enhanced styling for pregnancy theme */
input {
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
}

label {
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
}

/* Soft glow effect on focus */
input:focus-visible {
  box-shadow: 0 0 0 3px rgba(248, 187, 208, 0.15);
}

/* Floating label animation when input has value */
input:focus + label,
input:not(:placeholder-shown) + label {
  transform: translateY(-50%) scale(0.9);
}

/* Custom placeholder styling */
input::placeholder {
  color: rgb(156, 163, 175);
  font-style: italic;
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