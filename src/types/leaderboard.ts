export interface DailyLeaderboardRecord {
  rank: number
  steps: number
  username: string
}

export interface LeaderboardRecord {
  name: string
  rank: number
  value: number
}

export interface PeriodLeaderboardRecord {
  averageSteps: number
  rank: number
  username: string
}

export interface Streak5kLeaderboardRecord {
  days: number
  rank: number
  username: string
}

export interface TeamLeaderboardRecord {
  averageSteps: number
  rank: number
  team: string
}
