<template>
  <div class="min-h-screen bg-background p-8">
    <div class="max-w-4xl mx-auto space-y-8">
      <h1 class="text-3xl font-bold text-foreground mb-8">Component Testing - Preggo UI</h1>
      
      <!-- Button Tests -->
      <div class="space-y-4">
        <h2 class="text-2xl font-semibold text-foreground">Buttons</h2>
        <div class="flex flex-wrap gap-4">
          <Button>Default Button</Button>
          <Button variant="pregnancy">Pregnancy Button</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button size="sm">Small</Button>
          <Button size="lg">Large</Button>
        </div>
      </div>

      <!-- Card Tests -->
      <div class="space-y-4">
        <h2 class="text-2xl font-semibold text-foreground">Cards</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Pregnancy Week 20</CardTitle>
              <CardDescription>Your baby is now the size of a banana!</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Your baby is developing rapidly. This week brings exciting milestones in your pregnancy journey.</p>
            </CardContent>
            <CardFooter>
              <Button variant="pregnancy" size="sm">View Details</Button>
            </CardFooter>
          </Card>

          <Card class="bg-gentle-mint/10 border-gentle-mint/20">
            <CardHeader>
              <CardTitle>Health Tracking</CardTitle>
              <CardDescription>Monitor your wellness</CardDescription>
            </CardHeader>
            <CardContent>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span>Water intake</span>
                  <Badge variant="health">8/8 glasses</Badge>
                </div>
                <Progress :model-value="100" class="bg-gentle-mint/20" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <!-- Input Tests -->
      <div class="space-y-4">
        <h2 class="text-2xl font-semibold text-foreground">Form Elements</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-4">
            <div>
              <Label for="baby-name">Baby Name Ideas</Label>
              <Input id="baby-name" placeholder="Enter a name you love..." />
            </div>
            <div>
              <Label for="notes">Pregnancy Notes</Label>
              <Textarea id="notes" placeholder="How are you feeling today?" rows="4" />
            </div>
          </div>
          <div class="space-y-4">
            <div>
              <Label>Mood Today</Label>
              <div class="flex gap-2 mt-2">
                <Badge variant="pregnancy">Happy</Badge>
                <Badge variant="milestone">Excited</Badge>
                <Badge variant="outline">Tired</Badge>
                <Badge variant="secondary">Anxious</Badge>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Progress Tests -->
      <div class="space-y-4">
        <h2 class="text-2xl font-semibold text-foreground">Progress Indicators</h2>
        <div class="space-y-4">
          <div>
            <div class="flex justify-between mb-2">
              <span>Pregnancy Progress</span>
              <span>20/40 weeks</span>
            </div>
            <Progress :model-value="50" />
          </div>
          <div>
            <div class="flex justify-between mb-2">
              <span>Daily Water Goal</span>
              <span>6/8 glasses</span>
            </div>
            <Progress :model-value="75" />
          </div>
        </div>
      </div>

      <!-- Tabs Tests -->
      <div class="space-y-4">
        <h2 class="text-2xl font-semibold text-foreground">Tabs</h2>
        <Tabs default-value="overview">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="health">Health</TabsTrigger>
            <TabsTrigger value="milestones">Milestones</TabsTrigger>
          </TabsList>
          <TabsContent value="overview">
            <Card>
              <CardContent class="pt-6">
                <p>Welcome to your pregnancy overview. Here you can see a summary of your journey.</p>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="health">
            <Card>
              <CardContent class="pt-6">
                <p>Track your health metrics, appointments, and wellness goals.</p>
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="milestones">
            <Card>
              <CardContent class="pt-6">
                <p>Celebrate your pregnancy milestones and baby's development.</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      <!-- Avatar Tests -->
      <div class="space-y-4">
        <h2 class="text-2xl font-semibold text-foreground">Avatars</h2>
        <div class="flex gap-4 items-center">
          <Avatar>
            <AvatarFallback class="bg-soft-pink text-gray-800">M</AvatarFallback>
          </Avatar>
          <Avatar>
            <AvatarFallback class="bg-gentle-mint text-gray-800">P</AvatarFallback>
          </Avatar>
          <Avatar>
            <AvatarFallback class="bg-muted-lavender text-gray-800">B</AvatarFallback>
          </Avatar>
        </div>
      </div>

      <!-- Toast Test -->
      <div class="space-y-4">
        <h2 class="text-2xl font-semibold text-foreground">Toast Messages</h2>
        <div class="space-y-2">
          <Toast variant="pregnancy">
            <p>🎉 Congratulations! You've reached week 20 of your pregnancy!</p>
          </Toast>
          <Toast variant="success">
            <p>✅ Daily water goal completed!</p>
          </Toast>
        </div>
      </div>

      <!-- Tooltip Test -->
      <div class="space-y-4">
        <h2 class="text-2xl font-semibold text-foreground">Tooltips</h2>
        <div>
          <Tooltip content="This tracks your baby's estimated size">
            <Button variant="outline">Hover for Baby Size Info</Button>
          </Tooltip>
        </div>
      </div>

      <!-- Dropdown Menu Test -->
      <div class="space-y-4">
        <h2 class="text-2xl font-semibold text-foreground">Dropdown Menu</h2>
        <DropdownMenu>
          <template #trigger="{ toggle }">
            <Button @click="toggle">Pregnancy Actions</Button>
          </template>
          <DropdownMenuItem>Log Symptoms</DropdownMenuItem>
          <DropdownMenuItem>Track Appointment</DropdownMenuItem>
          <DropdownMenuItem>Add Milestone</DropdownMenuItem>
          <DropdownMenuItem>View Calendar</DropdownMenuItem>
        </DropdownMenu>
      </div>

      <!-- Custom Pregnancy Components -->
      <div class="space-y-4">
        <h2 class="text-2xl font-semibold text-foreground">Custom Pregnancy Components</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <PregnancyCard 
            title="Baby Development" 
            description="Week 20 - Halfway there!"
          >
            <p class="text-gray-700">Your baby is now about 10 inches long and weighs around 10.5 ounces. The baby can hear sounds from outside the womb!</p>
            <template #footer>
              <Button variant="pregnancy" size="sm">Learn More</Button>
            </template>
          </PregnancyCard>

          <div class="space-y-4">
            <MilestoneProgress
              title="Pregnancy Journey"
              subtitle="You're halfway through!"
              :current="20"
              :total="40"
              unit="weeks"
              :milestones="[12, 20, 28, 36]"
              show-milestones
              message="🎉 You've reached the halfway point of your pregnancy!"
            />
            
            <MilestoneProgress
              title="Daily Water Intake"
              subtitle="Stay hydrated for you and baby"
              :current="6"
              :total="8"
              unit="glasses"
              message="Great job! Keep up the good hydration habits."
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Import all the UI components
import Button from '~/components/ui/Button.vue'
import Card from '~/components/ui/Card.vue'
import CardHeader from '~/components/ui/CardHeader.vue'
import CardTitle from '~/components/ui/CardTitle.vue'
import CardDescription from '~/components/ui/CardDescription.vue'
import CardContent from '~/components/ui/CardContent.vue'
import CardFooter from '~/components/ui/CardFooter.vue'
import Input from '~/components/ui/Input.vue'
import Label from '~/components/ui/Label.vue'
import Textarea from '~/components/ui/Textarea.vue'
import Badge from '~/components/ui/Badge.vue'
import Progress from '~/components/ui/Progress.vue'
import Tabs from '~/components/ui/Tabs.vue'
import TabsList from '~/components/ui/TabsList.vue'
import TabsTrigger from '~/components/ui/TabsTrigger.vue'
import TabsContent from '~/components/ui/TabsContent.vue'
import Avatar from '~/components/ui/Avatar.vue'
import AvatarFallback from '~/components/ui/AvatarFallback.vue'
import Toast from '~/components/ui/Toast.vue'
import Tooltip from '~/components/ui/Tooltip.vue'
import DropdownMenu from '~/components/ui/DropdownMenu.vue'
import DropdownMenuItem from '~/components/ui/DropdownMenuItem.vue'
import PregnancyCard from '~/components/ui/PregnancyCard.vue'
import MilestoneProgress from '~/components/ui/MilestoneProgress.vue'

// Set page meta
definePageMeta({
  title: 'Component Testing - Preggo UI'
})
</script>