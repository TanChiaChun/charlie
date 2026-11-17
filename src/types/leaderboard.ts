export interface DailyLeaderboardRecord {
  rank: number
  steps: number
  username: string
}

export interface LeaderboardRecord {
  rank: number
  username: string
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
