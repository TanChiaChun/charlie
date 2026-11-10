export interface LeaderboardRecord {
  rank: number
  value: number
  username: string
}

export interface DailyLeaderboardRecord {
  rank: number
  steps: number
  username: string
}

export interface PeriodLeaderboardRecord {
  rank: number
  averageSteps: number
  username: string
}

export interface Streak5kLeaderboardRecord {
  rank: number
  days: number
  username: string
}
