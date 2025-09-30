export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "13.0.4"
  }
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          extensions?: Json
          operationName?: string
          query?: string
          variables?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      access_levels: {
        Row: {
          created_at: string
          description: string | null
          id: string
          name: string
        }
        Insert: {
          created_at?: string
          description?: string | null
          id?: string
          name: string
        }
        Update: {
          created_at?: string
          description?: string | null
          id?: string
          name?: string
        }
        Relationships: []
      }
      assignments: {
        Row: {
          assignmentReason: string | null
          assignmentType: Database["public"]["Enums"]["assignments_assignmenttype_enum"]
          coachId: string | null
          dateAssigned: string | null
          dateEnded: string | null
          employmentType: string | null
          endDate: string | null
          fellowId: string | null
          id: string
          placedByTTN: boolean
          placementType: string | null
          principalContactNumber: string | null
          principalEmail: string | null
          principalName: string | null
          reasonEnded: string | null
          schoolId: string | null
          startDate: string | null
          teachingStatus: string | null
        }
        Insert: {
          assignmentReason?: string | null
          assignmentType?: Database["public"]["Enums"]["assignments_assignmenttype_enum"]
          coachId?: string | null
          dateAssigned?: string | null
          dateEnded?: string | null
          employmentType?: string | null
          endDate?: string | null
          fellowId?: string | null
          id?: string
          placedByTTN?: boolean
          placementType?: string | null
          principalContactNumber?: string | null
          principalEmail?: string | null
          principalName?: string | null
          reasonEnded?: string | null
          schoolId?: string | null
          startDate?: string | null
          teachingStatus?: string | null
        }
        Update: {
          assignmentReason?: string | null
          assignmentType?: Database["public"]["Enums"]["assignments_assignmenttype_enum"]
          coachId?: string | null
          dateAssigned?: string | null
          dateEnded?: string | null
          employmentType?: string | null
          endDate?: string | null
          fellowId?: string | null
          id?: string
          placedByTTN?: boolean
          placementType?: string | null
          principalContactNumber?: string | null
          principalEmail?: string | null
          principalName?: string | null
          reasonEnded?: string | null
          schoolId?: string | null
          startDate?: string | null
          teachingStatus?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "FK_b043dde1162085a4f07bbde8b10"
            columns: ["schoolId"]
            isOneToOne: false
            referencedRelation: "schools_dev"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "FK_e18095e49588c86f93a9b72e006"
            columns: ["coachId"]
            isOneToOne: false
            referencedRelation: "coaches_dev"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "FK_e33959dfb7f0b9f0eeded2c0402"
            columns: ["fellowId"]
            isOneToOne: false
            referencedRelation: "fellows_dev"
            referencedColumns: ["id"]
          },
        ]
      }
      class_assignments: {
        Row: {
          class_size: number
          created_at: string | null
          fellow_id: string
          grade: number
          id: string
          learners: number
          phase: string
          school_assignment_id: string
        }
        Insert: {
          class_size: number
          created_at?: string | null
          fellow_id: string
          grade: number
          id?: string
          learners: number
          phase: string
          school_assignment_id: string
        }
        Update: {
          class_size?: number
          created_at?: string | null
          fellow_id?: string
          grade?: number
          id?: string
          learners?: number
          phase?: string
          school_assignment_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "class_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "class_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "class_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellows"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "class_assignments_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["school_assignment_id"]
          },
          {
            foreignKeyName: "class_assignments_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["school_assignment_id"]
          },
          {
            foreignKeyName: "class_assignments_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "school_assignments"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "class_assignments_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "vw_school_assignments"
            referencedColumns: ["assignment_id"]
          },
        ]
      }
      class_data_staging: {
        Row: {
          class_name: string | null
          class_no: string | null
          class_size: number | null
          coach_name: string | null
          coaching_priority: string | null
          created_at: string | null
          data_quality_flag: string | null
          exclusion_reason: string | null
          fellow_name: string | null
          grade: string | null
          grade_cleaned: string | null
          id: string
          inclusion_status: string | null
          missing_data_flags: string[] | null
          phase: string | null
          phase_cleaned: string | null
          subject: string | null
          subject_category: string | null
          subject_category_cleaned: string | null
          subject_cleaned: string | null
          term_1_mark: number | null
          term_2_mark: number | null
          updated_at: string | null
        }
        Insert: {
          class_name?: string | null
          class_no?: string | null
          class_size?: number | null
          coach_name?: string | null
          coaching_priority?: string | null
          created_at?: string | null
          data_quality_flag?: string | null
          exclusion_reason?: string | null
          fellow_name?: string | null
          grade?: string | null
          grade_cleaned?: string | null
          id?: string
          inclusion_status?: string | null
          missing_data_flags?: string[] | null
          phase?: string | null
          phase_cleaned?: string | null
          subject?: string | null
          subject_category?: string | null
          subject_category_cleaned?: string | null
          subject_cleaned?: string | null
          term_1_mark?: number | null
          term_2_mark?: number | null
          updated_at?: string | null
        }
        Update: {
          class_name?: string | null
          class_no?: string | null
          class_size?: number | null
          coach_name?: string | null
          coaching_priority?: string | null
          created_at?: string | null
          data_quality_flag?: string | null
          exclusion_reason?: string | null
          fellow_name?: string | null
          grade?: string | null
          grade_cleaned?: string | null
          id?: string
          inclusion_status?: string | null
          missing_data_flags?: string[] | null
          phase?: string | null
          phase_cleaned?: string | null
          subject?: string | null
          subject_category?: string | null
          subject_category_cleaned?: string | null
          subject_cleaned?: string | null
          term_1_mark?: number | null
          term_2_mark?: number | null
          updated_at?: string | null
        }
        Relationships: []
      }
      classes: {
        Row: {
          class_name: string | null
          class_size: number | null
          created_at: string | null
          fellow_name: string
          grade: string
          id: string
          language: string | null
          updated_at: string | null
        }
        Insert: {
          class_name?: string | null
          class_size?: number | null
          created_at?: string | null
          fellow_name: string
          grade: string
          id?: string
          language?: string | null
          updated_at?: string | null
        }
        Update: {
          class_name?: string | null
          class_size?: number | null
          created_at?: string | null
          fellow_name?: string
          grade?: string
          id?: string
          language?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      classrooms: {
        Row: {
          class_name: string
          class_size: number | null
          created_at: string | null
          data_source: string | null
          fellow_name: string
          grade: string | null
          id: string
          placement_id: string
          subject: string | null
          updated_at: string | null
        }
        Insert: {
          class_name: string
          class_size?: number | null
          created_at?: string | null
          data_source?: string | null
          fellow_name: string
          grade?: string | null
          id?: string
          placement_id: string
          subject?: string | null
          updated_at?: string | null
        }
        Update: {
          class_name?: string
          class_size?: number | null
          created_at?: string | null
          data_source?: string | null
          fellow_name?: string
          grade?: string | null
          id?: string
          placement_id?: string
          subject?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fk_classrooms_placement"
            columns: ["placement_id"]
            isOneToOne: false
            referencedRelation: "school_placements"
            referencedColumns: ["id"]
          },
        ]
      }
      coach_academic_results: {
        Row: {
          annual_avg: number | null
          class_name: string | null
          class_no: string | null
          class_size: number | null
          coach_id: string | null
          created_at: string | null
          fellow_id: string | null
          fellow_name: string
          fellowship_year: number | null
          grade: string | null
          id: string
          subject: string | null
          term_1_avg: number | null
          term_2_avg: number | null
          term_3_avg: number | null
          term_4_avg: number | null
          term_collected: number
          updated_at: string | null
        }
        Insert: {
          annual_avg?: number | null
          class_name?: string | null
          class_no?: string | null
          class_size?: number | null
          coach_id?: string | null
          created_at?: string | null
          fellow_id?: string | null
          fellow_name: string
          fellowship_year?: number | null
          grade?: string | null
          id?: string
          subject?: string | null
          term_1_avg?: number | null
          term_2_avg?: number | null
          term_3_avg?: number | null
          term_4_avg?: number | null
          term_collected: number
          updated_at?: string | null
        }
        Update: {
          annual_avg?: number | null
          class_name?: string | null
          class_no?: string | null
          class_size?: number | null
          coach_id?: string | null
          created_at?: string | null
          fellow_id?: string | null
          fellow_name?: string
          fellowship_year?: number | null
          grade?: string | null
          id?: string
          subject?: string | null
          term_1_avg?: number | null
          term_2_avg?: number | null
          term_3_avg?: number | null
          term_4_avg?: number | null
          term_collected?: number
          updated_at?: string | null
        }
        Relationships: []
      }
      coach_assignments: {
        Row: {
          assigned_by: string | null
          assignment_end: string | null
          assignment_start: string | null
          coach_id: string
          created_at: string
          fellow_id: string
          id: string
          is_active: boolean
        }
        Insert: {
          assigned_by?: string | null
          assignment_end?: string | null
          assignment_start?: string | null
          coach_id: string
          created_at?: string
          fellow_id: string
          id?: string
          is_active?: boolean
        }
        Update: {
          assigned_by?: string | null
          assignment_end?: string | null
          assignment_start?: string | null
          coach_id?: string
          created_at?: string
          fellow_id?: string
          id?: string
          is_active?: boolean
        }
        Relationships: [
          {
            foreignKeyName: "coach_assignments_coach_id_fkey"
            columns: ["coach_id"]
            isOneToOne: false
            referencedRelation: "coaches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "coach_assignments_coach_id_fkey"
            columns: ["coach_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["coach_id"]
          },
          {
            foreignKeyName: "coach_assignments_coach_id_fkey"
            columns: ["coach_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["coach_id"]
          },
          {
            foreignKeyName: "coach_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "coach_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "coach_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellows"
            referencedColumns: ["id"]
          },
        ]
      }
      coaches: {
        Row: {
          coach_name: string
          coach_type: string | null
          created_at: string
          email: string | null
          id: string
          is_active: boolean | null
        }
        Insert: {
          coach_name: string
          coach_type?: string | null
          created_at?: string
          email?: string | null
          id?: string
          is_active?: boolean | null
        }
        Update: {
          coach_name?: string
          coach_type?: string | null
          created_at?: string
          email?: string | null
          id?: string
          is_active?: boolean | null
        }
        Relationships: []
      }
      coaches_dev: {
        Row: {
          dateOfBirth: string | null
          email: string
          fullName: string
          gender: string | null
          id: string
          phoneNumber: string | null
          provinceOfOrigin: string | null
          status: string | null
          suburb: string | null
        }
        Insert: {
          dateOfBirth?: string | null
          email: string
          fullName: string
          gender?: string | null
          id?: string
          phoneNumber?: string | null
          provinceOfOrigin?: string | null
          status?: string | null
          suburb?: string | null
        }
        Update: {
          dateOfBirth?: string | null
          email?: string
          fullName?: string
          gender?: string | null
          id?: string
          phoneNumber?: string | null
          provinceOfOrigin?: string | null
          status?: string | null
          suburb?: string | null
        }
        Relationships: []
      }
      coaching_session_attendance: {
        Row: {
          actual_reason: string | null
          attended: boolean | null
          coach: string | null
          coaching_session_no: number | null
          created_at: string | null
          date_scheduled: string | null
          fellow_id: string
          fellow_name: string | null
          id: string
          reason_provided: boolean | null
          term: string | null
          updated_at: string | null
        }
        Insert: {
          actual_reason?: string | null
          attended?: boolean | null
          coach?: string | null
          coaching_session_no?: number | null
          created_at?: string | null
          date_scheduled?: string | null
          fellow_id: string
          fellow_name?: string | null
          id?: string
          reason_provided?: boolean | null
          term?: string | null
          updated_at?: string | null
        }
        Update: {
          actual_reason?: string | null
          attended?: boolean | null
          coach?: string | null
          coaching_session_no?: number | null
          created_at?: string | null
          date_scheduled?: string | null
          fellow_id?: string
          fellow_name?: string | null
          id?: string
          reason_provided?: boolean | null
          term?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "coaching_session_attendance_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_demographics"
            referencedColumns: ["id"]
          },
        ]
      }
      collective_impact: {
        Row: {
          coach: string
          comments: string | null
          created_at: string | null
          fellow_id: string
          fellow_name: string | null
          id: string
          status: string | null
          theme: string | null
          updated_at: string | null
        }
        Insert: {
          coach: string
          comments?: string | null
          created_at?: string | null
          fellow_id: string
          fellow_name?: string | null
          id?: string
          status?: string | null
          theme?: string | null
          updated_at?: string | null
        }
        Update: {
          coach?: string
          comments?: string | null
          created_at?: string | null
          fellow_id?: string
          fellow_name?: string | null
          id?: string
          status?: string | null
          theme?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "collective_impact_fellow_id_fkey1"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_demographics"
            referencedColumns: ["id"]
          },
        ]
      }
      cycle_coaches: {
        Row: {
          coach_id: string
          coach_type: string | null
          created_at: string | null
          fellowship_cycle_id: string
          id: string
          is_active: boolean | null
          notes: string | null
        }
        Insert: {
          coach_id: string
          coach_type?: string | null
          created_at?: string | null
          fellowship_cycle_id: string
          id?: string
          is_active?: boolean | null
          notes?: string | null
        }
        Update: {
          coach_id?: string
          coach_type?: string | null
          created_at?: string | null
          fellowship_cycle_id?: string
          id?: string
          is_active?: boolean | null
          notes?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "cycle_coaches_coach_id_fkey"
            columns: ["coach_id"]
            isOneToOne: false
            referencedRelation: "coaches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "cycle_coaches_coach_id_fkey"
            columns: ["coach_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["coach_id"]
          },
          {
            foreignKeyName: "cycle_coaches_coach_id_fkey"
            columns: ["coach_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["coach_id"]
          },
          {
            foreignKeyName: "cycle_coaches_fellowship_cycle_id_fkey"
            columns: ["fellowship_cycle_id"]
            isOneToOne: false
            referencedRelation: "fellowship_cycles"
            referencedColumns: ["id"]
          },
        ]
      }
      data_quality_issues: {
        Row: {
          action_required: string | null
          class_name: string | null
          coach: string | null
          cohort_number: number | null
          created_at: string | null
          fellow_name: string | null
          grade: string | null
          id: string
          issue_description: string | null
          issue_type: string
          priority_level: string | null
          resolved: boolean | null
          subject: string | null
          updated_at: string | null
        }
        Insert: {
          action_required?: string | null
          class_name?: string | null
          coach?: string | null
          cohort_number?: number | null
          created_at?: string | null
          fellow_name?: string | null
          grade?: string | null
          id?: string
          issue_description?: string | null
          issue_type: string
          priority_level?: string | null
          resolved?: boolean | null
          subject?: string | null
          updated_at?: string | null
        }
        Update: {
          action_required?: string | null
          class_name?: string | null
          coach?: string | null
          cohort_number?: number | null
          created_at?: string | null
          fellow_name?: string | null
          grade?: string | null
          id?: string
          issue_description?: string | null
          issue_type?: string
          priority_level?: string | null
          resolved?: boolean | null
          subject?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      domain_scores: {
        Row: {
          classification: string | null
          domain: string
          domain_avg: number | null
          observation_id: string
          strongest_tier: string | null
          tier1_score: number | null
          tier2_score: number | null
          tier3_score: number | null
          weakest_tier: string | null
        }
        Insert: {
          classification?: string | null
          domain: string
          domain_avg?: number | null
          observation_id: string
          strongest_tier?: string | null
          tier1_score?: number | null
          tier2_score?: number | null
          tier3_score?: number | null
          weakest_tier?: string | null
        }
        Update: {
          classification?: string | null
          domain?: string
          domain_avg?: number | null
          observation_id?: string
          strongest_tier?: string | null
          tier1_score?: number | null
          tier2_score?: number | null
          tier3_score?: number | null
          weakest_tier?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "domain_scores_observation_id_fkey"
            columns: ["observation_id"]
            isOneToOne: false
            referencedRelation: "observations"
            referencedColumns: ["observation_id"]
          },
          {
            foreignKeyName: "domain_scores_observation_id_fkey"
            columns: ["observation_id"]
            isOneToOne: false
            referencedRelation: "v_observation_full"
            referencedColumns: ["observation_id"]
          },
        ]
      }
      domains: {
        Row: {
          domain_code: string
          domain_description: string
          domain_name: string
        }
        Insert: {
          domain_code: string
          domain_description: string
          domain_name: string
        }
        Update: {
          domain_code?: string
          domain_description?: string
          domain_name?: string
        }
        Relationships: []
      }
      educator_profiles: {
        Row: {
          created_at: string | null
          fellow_id: string | null
          id: string
          institution: string | null
          phase_specialisations: string[] | null
          qualification_type: string | null
          sace_number: string | null
          sace_registered: boolean | null
          subject_specialisations: string[] | null
          teaching_experience: string | null
        }
        Insert: {
          created_at?: string | null
          fellow_id?: string | null
          id?: string
          institution?: string | null
          phase_specialisations?: string[] | null
          qualification_type?: string | null
          sace_number?: string | null
          sace_registered?: boolean | null
          subject_specialisations?: string[] | null
          teaching_experience?: string | null
        }
        Update: {
          created_at?: string | null
          fellow_id?: string | null
          id?: string
          institution?: string | null
          phase_specialisations?: string[] | null
          qualification_type?: string | null
          sace_number?: string | null
          sace_registered?: boolean | null
          subject_specialisations?: string[] | null
          teaching_experience?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "educator_profiles_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: true
            referencedRelation: "fellow_profile"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "educator_profiles_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: true
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "educator_profiles_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: true
            referencedRelation: "fellows"
            referencedColumns: ["id"]
          },
        ]
      }
      entities: {
        Row: {
          created_at: string
          description: string | null
          entity_type: string
          id: string
          is_active: boolean
          name: string
          nav_label: string
        }
        Insert: {
          created_at?: string
          description?: string | null
          entity_type: string
          id?: string
          is_active?: boolean
          name: string
          nav_label: string
        }
        Update: {
          created_at?: string
          description?: string | null
          entity_type?: string
          id?: string
          is_active?: boolean
          name?: string
          nav_label?: string
        }
        Relationships: []
      }
      feedback: {
        Row: {
          additional_comments: string | null
          areas_for_improvement: string | null
          created_at: string | null
          feedback_id: string
          next_steps: string | null
          observation_id: string
          overall_effectiveness: number | null
          strengths: string | null
        }
        Insert: {
          additional_comments?: string | null
          areas_for_improvement?: string | null
          created_at?: string | null
          feedback_id?: string
          next_steps?: string | null
          observation_id: string
          overall_effectiveness?: number | null
          strengths?: string | null
        }
        Update: {
          additional_comments?: string | null
          areas_for_improvement?: string | null
          created_at?: string | null
          feedback_id?: string
          next_steps?: string | null
          observation_id?: string
          overall_effectiveness?: number | null
          strengths?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "feedback_observationId_fkey"
            columns: ["observation_id"]
            isOneToOne: false
            referencedRelation: "observations"
            referencedColumns: ["observation_id"]
          },
          {
            foreignKeyName: "feedback_observationId_fkey"
            columns: ["observation_id"]
            isOneToOne: false
            referencedRelation: "v_observation_full"
            referencedColumns: ["observation_id"]
          },
        ]
      }
      fellow_bio: {
        Row: {
          action_required: string | null
          cellphone_number: string | null
          coach: string | null
          cohort_number: number | null
          created_at: string | null
          data_completeness_flag: string | null
          date_of_birth: string | null
          email_address: string | null
          fellow_name: string
          fellow_status: string | null
          gender: string | null
          has_class_data: boolean | null
          id: string
          partnered_to: string | null
          placed_by_ttn: boolean | null
          principal_name: string | null
          principal_school_contact: string | null
          principal_school_email: string | null
          province_of_origin: string | null
          race: string | null
          school_address: string | null
          school_name: string | null
          school_province: string | null
          school_type: string | null
          suburb: string | null
          teaching_status: string | null
          updated_at: string | null
          year_of_entry_into_program: number | null
          year_of_fellowship: number | null
        }
        Insert: {
          action_required?: string | null
          cellphone_number?: string | null
          coach?: string | null
          cohort_number?: number | null
          created_at?: string | null
          data_completeness_flag?: string | null
          date_of_birth?: string | null
          email_address?: string | null
          fellow_name: string
          fellow_status?: string | null
          gender?: string | null
          has_class_data?: boolean | null
          id?: string
          partnered_to?: string | null
          placed_by_ttn?: boolean | null
          principal_name?: string | null
          principal_school_contact?: string | null
          principal_school_email?: string | null
          province_of_origin?: string | null
          race?: string | null
          school_address?: string | null
          school_name?: string | null
          school_province?: string | null
          school_type?: string | null
          suburb?: string | null
          teaching_status?: string | null
          updated_at?: string | null
          year_of_entry_into_program?: number | null
          year_of_fellowship?: number | null
        }
        Update: {
          action_required?: string | null
          cellphone_number?: string | null
          coach?: string | null
          cohort_number?: number | null
          created_at?: string | null
          data_completeness_flag?: string | null
          date_of_birth?: string | null
          email_address?: string | null
          fellow_name?: string
          fellow_status?: string | null
          gender?: string | null
          has_class_data?: boolean | null
          id?: string
          partnered_to?: string | null
          placed_by_ttn?: boolean | null
          principal_name?: string | null
          principal_school_contact?: string | null
          principal_school_email?: string | null
          province_of_origin?: string | null
          race?: string | null
          school_address?: string | null
          school_name?: string | null
          school_province?: string | null
          school_type?: string | null
          suburb?: string | null
          teaching_status?: string | null
          updated_at?: string | null
          year_of_entry_into_program?: number | null
          year_of_fellowship?: number | null
        }
        Relationships: []
      }
      fellow_bio_coach_report: {
        Row: {
          assignment_reason: string | null
          cellphone_number: string | null
          coach: string | null
          cohort_number: number | null
          created_at: string
          date_assigned: string | null
          date_ended: string | null
          dob: string | null
          email_address: string | null
          fellow_name: string
          fellow_status: string | null
          gender: string | null
          id: string
          placed_by_ttn: string | null
          principal_contact_number: string | null
          principal_email: string | null
          principal_name: string | null
          province_of_origin: string | null
          race: string | null
          reason_ended: string | null
          report_term: number
          school_address: string | null
          school_name: string | null
          school_province: string | null
          school_type: string | null
          suburb: string | null
          teaching_status: string | null
          year_of_entry: number | null
          year_of_fellowship: number | null
        }
        Insert: {
          assignment_reason?: string | null
          cellphone_number?: string | null
          coach?: string | null
          cohort_number?: number | null
          created_at?: string
          date_assigned?: string | null
          date_ended?: string | null
          dob?: string | null
          email_address?: string | null
          fellow_name: string
          fellow_status?: string | null
          gender?: string | null
          id?: string
          placed_by_ttn?: string | null
          principal_contact_number?: string | null
          principal_email?: string | null
          principal_name?: string | null
          province_of_origin?: string | null
          race?: string | null
          reason_ended?: string | null
          report_term: number
          school_address?: string | null
          school_name?: string | null
          school_province?: string | null
          school_type?: string | null
          suburb?: string | null
          teaching_status?: string | null
          year_of_entry?: number | null
          year_of_fellowship?: number | null
        }
        Update: {
          assignment_reason?: string | null
          cellphone_number?: string | null
          coach?: string | null
          cohort_number?: number | null
          created_at?: string
          date_assigned?: string | null
          date_ended?: string | null
          dob?: string | null
          email_address?: string | null
          fellow_name?: string
          fellow_status?: string | null
          gender?: string | null
          id?: string
          placed_by_ttn?: string | null
          principal_contact_number?: string | null
          principal_email?: string | null
          principal_name?: string | null
          province_of_origin?: string | null
          race?: string | null
          reason_ended?: string | null
          report_term?: number
          school_address?: string | null
          school_name?: string | null
          school_province?: string | null
          school_type?: string | null
          suburb?: string | null
          teaching_status?: string | null
          year_of_entry?: number | null
          year_of_fellowship?: number | null
        }
        Relationships: []
      }
      fellow_changes: {
        Row: {
          changed_at: string | null
          fellow_id: string
          field_name: string
          id: string
          new_value: string | null
          old_value: string | null
          source: string | null
        }
        Insert: {
          changed_at?: string | null
          fellow_id: string
          field_name: string
          id?: string
          new_value?: string | null
          old_value?: string | null
          source?: string | null
        }
        Update: {
          changed_at?: string | null
          fellow_id?: string
          field_name?: string
          id?: string
          new_value?: string | null
          old_value?: string | null
          source?: string | null
        }
        Relationships: []
      }
      fellow_demographics: {
        Row: {
          cellphone_number: string | null
          coach_name: string | null
          cohort_number: string
          created_at: string | null
          data_source: string | null
          date_of_birth: string | null
          email_address: string
          entry_year: number
          fellow_name: string
          fellow_status: string
          fellowship_year: number
          gender: string | null
          id: string
          partner_organization: string | null
          province_of_origin: string | null
          race: string | null
          suburb: string | null
          updated_at: string | null
        }
        Insert: {
          cellphone_number?: string | null
          coach_name?: string | null
          cohort_number: string
          created_at?: string | null
          data_source?: string | null
          date_of_birth?: string | null
          email_address: string
          entry_year: number
          fellow_name: string
          fellow_status: string
          fellowship_year: number
          gender?: string | null
          id?: string
          partner_organization?: string | null
          province_of_origin?: string | null
          race?: string | null
          suburb?: string | null
          updated_at?: string | null
        }
        Update: {
          cellphone_number?: string | null
          coach_name?: string | null
          cohort_number?: string
          created_at?: string | null
          data_source?: string | null
          date_of_birth?: string | null
          email_address?: string
          entry_year?: number
          fellow_name?: string
          fellow_status?: string
          fellowship_year?: number
          gender?: string | null
          id?: string
          partner_organization?: string | null
          province_of_origin?: string | null
          race?: string | null
          suburb?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      fellow_engagement: {
        Row: {
          created_at: string | null
          engagement_rate: number | null
          event: string | null
          fellow_id: string
          fellow_name: string | null
          id: string
          term: string | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          engagement_rate?: number | null
          event?: string | null
          fellow_id: string
          fellow_name?: string | null
          id?: string
          term?: string | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          engagement_rate?: number | null
          event?: string | null
          fellow_id?: string
          fellow_name?: string | null
          id?: string
          term?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fellow_engagement_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_demographics"
            referencedColumns: ["id"]
          },
        ]
      }
      fellow_stage: {
        Row: {
          area: string | null
          assignment_reason: string | null
          cellphone_number: string | null
          coach: string | null
          cohort_number: string | null
          date_assigned: string | null
          date_ended: string | null
          dob: string | null
          email_address: string | null
          fellow_id: string | null
          fellow_name: string | null
          fellow_status: string | null
          fet_phase: string | null
          foundation_phase: string | null
          gender: string | null
          grade_1: string | null
          grade_10: string | null
          grade_11: string | null
          grade_12: string | null
          grade_2: string | null
          grade_3: string | null
          grade_4: string | null
          grade_5: string | null
          grade_6: string | null
          grade_7: string | null
          grade_8: string | null
          grade_9: string | null
          grade_list: string | null
          intermediate_phase: string | null
          language_of_teaching: string | null
          phase: string | null
          placed_by_ttn: string | null
          principal_contact_number: string | null
          principal_email: string | null
          principal_name: string | null
          province_of_origin: string | null
          race: string | null
          reason_ended: string | null
          school_address: string | null
          school_name: string | null
          school_province: string | null
          school_type: string | null
          senior_phase: string | null
          subjects: string | null
          suburb: string | null
          teaching_status: string | null
          year_of_entry: string | null
          year_of_fellowship: string | null
        }
        Insert: {
          area?: string | null
          assignment_reason?: string | null
          cellphone_number?: string | null
          coach?: string | null
          cohort_number?: string | null
          date_assigned?: string | null
          date_ended?: string | null
          dob?: string | null
          email_address?: string | null
          fellow_id?: string | null
          fellow_name?: string | null
          fellow_status?: string | null
          fet_phase?: string | null
          foundation_phase?: string | null
          gender?: string | null
          grade_1?: string | null
          grade_10?: string | null
          grade_11?: string | null
          grade_12?: string | null
          grade_2?: string | null
          grade_3?: string | null
          grade_4?: string | null
          grade_5?: string | null
          grade_6?: string | null
          grade_7?: string | null
          grade_8?: string | null
          grade_9?: string | null
          grade_list?: string | null
          intermediate_phase?: string | null
          language_of_teaching?: string | null
          phase?: string | null
          placed_by_ttn?: string | null
          principal_contact_number?: string | null
          principal_email?: string | null
          principal_name?: string | null
          province_of_origin?: string | null
          race?: string | null
          reason_ended?: string | null
          school_address?: string | null
          school_name?: string | null
          school_province?: string | null
          school_type?: string | null
          senior_phase?: string | null
          subjects?: string | null
          suburb?: string | null
          teaching_status?: string | null
          year_of_entry?: string | null
          year_of_fellowship?: string | null
        }
        Update: {
          area?: string | null
          assignment_reason?: string | null
          cellphone_number?: string | null
          coach?: string | null
          cohort_number?: string | null
          date_assigned?: string | null
          date_ended?: string | null
          dob?: string | null
          email_address?: string | null
          fellow_id?: string | null
          fellow_name?: string | null
          fellow_status?: string | null
          fet_phase?: string | null
          foundation_phase?: string | null
          gender?: string | null
          grade_1?: string | null
          grade_10?: string | null
          grade_11?: string | null
          grade_12?: string | null
          grade_2?: string | null
          grade_3?: string | null
          grade_4?: string | null
          grade_5?: string | null
          grade_6?: string | null
          grade_7?: string | null
          grade_8?: string | null
          grade_9?: string | null
          grade_list?: string | null
          intermediate_phase?: string | null
          language_of_teaching?: string | null
          phase?: string | null
          placed_by_ttn?: string | null
          principal_contact_number?: string | null
          principal_email?: string | null
          principal_name?: string | null
          province_of_origin?: string | null
          race?: string | null
          reason_ended?: string | null
          school_address?: string | null
          school_name?: string | null
          school_province?: string | null
          school_type?: string | null
          senior_phase?: string | null
          subjects?: string | null
          suburb?: string | null
          teaching_status?: string | null
          year_of_entry?: string | null
          year_of_fellowship?: string | null
        }
        Relationships: []
      }
      fellows: {
        Row: {
          cellphone: string
          coach_assignment_id: string | null
          cohort_name: string | null
          created_at: string | null
          date_of_birth: string | null
          educator_profile_id: string | null
          email: string
          fellow_category: string | null
          full_name: string
          gender: string | null
          id: string
          id_number: string | null
          partner_organization: string | null
          province_of_origin: string
          race: string | null
          school_assignment_id: string | null
          status: string
          updated_at: string | null
          year_of_entry: string
          year_of_fellowship: number
        }
        Insert: {
          cellphone: string
          coach_assignment_id?: string | null
          cohort_name?: string | null
          created_at?: string | null
          date_of_birth?: string | null
          educator_profile_id?: string | null
          email: string
          fellow_category?: string | null
          full_name: string
          gender?: string | null
          id?: string
          id_number?: string | null
          partner_organization?: string | null
          province_of_origin: string
          race?: string | null
          school_assignment_id?: string | null
          status: string
          updated_at?: string | null
          year_of_entry: string
          year_of_fellowship: number
        }
        Update: {
          cellphone?: string
          coach_assignment_id?: string | null
          cohort_name?: string | null
          created_at?: string | null
          date_of_birth?: string | null
          educator_profile_id?: string | null
          email?: string
          fellow_category?: string | null
          full_name?: string
          gender?: string | null
          id?: string
          id_number?: string | null
          partner_organization?: string | null
          province_of_origin?: string
          race?: string | null
          school_assignment_id?: string | null
          status?: string
          updated_at?: string | null
          year_of_entry?: string
          year_of_fellowship?: number
        }
        Relationships: [
          {
            foreignKeyName: "fellows_coach_assignment_id_fkey"
            columns: ["coach_assignment_id"]
            isOneToOne: false
            referencedRelation: "coach_assignments"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "fellows_coach_assignment_id_fkey"
            columns: ["coach_assignment_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["coach_assignment_id"]
          },
          {
            foreignKeyName: "fellows_coach_assignment_id_fkey"
            columns: ["coach_assignment_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["coach_assignment_id"]
          },
          {
            foreignKeyName: "fellows_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["school_assignment_id"]
          },
          {
            foreignKeyName: "fellows_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["school_assignment_id"]
          },
          {
            foreignKeyName: "fellows_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "school_assignments"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "fellows_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "vw_school_assignments"
            referencedColumns: ["assignment_id"]
          },
        ]
      }
      fellows_dev: {
        Row: {
          cellphoneNumber: string | null
          cohort: string | null
          dateOfBirth: string | null
          emailAddress: string
          fellowStatus: string | null
          fullName: string
          gender: string | null
          graduationYear: number | null
          id: string
          institution: string | null
          partnerOrg: string | null
          phaseSpecialization:
            | Database["public"]["Enums"]["fellows_dev_phasespecialization_enum"]
            | null
          placedByTTN: boolean
          provinceOfOrigin: string | null
          qualificationType: Database["public"]["Enums"]["fellows_dev_qualificationtype_enum"]
          race: string | null
          saceNumber: string | null
          subjectSpecializations: string | null
          suburb: string | null
          teachingExperienceYears: number | null
          yearOfEntry: number | null
          yearOfFellowship: number | null
        }
        Insert: {
          cellphoneNumber?: string | null
          cohort?: string | null
          dateOfBirth?: string | null
          emailAddress: string
          fellowStatus?: string | null
          fullName: string
          gender?: string | null
          graduationYear?: number | null
          id?: string
          institution?: string | null
          partnerOrg?: string | null
          phaseSpecialization?:
            | Database["public"]["Enums"]["fellows_dev_phasespecialization_enum"]
            | null
          placedByTTN?: boolean
          provinceOfOrigin?: string | null
          qualificationType: Database["public"]["Enums"]["fellows_dev_qualificationtype_enum"]
          race?: string | null
          saceNumber?: string | null
          subjectSpecializations?: string | null
          suburb?: string | null
          teachingExperienceYears?: number | null
          yearOfEntry?: number | null
          yearOfFellowship?: number | null
        }
        Update: {
          cellphoneNumber?: string | null
          cohort?: string | null
          dateOfBirth?: string | null
          emailAddress?: string
          fellowStatus?: string | null
          fullName?: string
          gender?: string | null
          graduationYear?: number | null
          id?: string
          institution?: string | null
          partnerOrg?: string | null
          phaseSpecialization?:
            | Database["public"]["Enums"]["fellows_dev_phasespecialization_enum"]
            | null
          placedByTTN?: boolean
          provinceOfOrigin?: string | null
          qualificationType?: Database["public"]["Enums"]["fellows_dev_qualificationtype_enum"]
          race?: string | null
          saceNumber?: string | null
          subjectSpecializations?: string | null
          suburb?: string | null
          teachingExperienceYears?: number | null
          yearOfEntry?: number | null
          yearOfFellowship?: number | null
        }
        Relationships: []
      }
      fellowship_cycles: {
        Row: {
          created_at: string | null
          cycle_year: number
          end_date: string
          id: string
          notes: string | null
          start_date: string
          status: Database["public"]["Enums"]["cycle_status"]
          term_count: number | null
        }
        Insert: {
          created_at?: string | null
          cycle_year: number
          end_date: string
          id?: string
          notes?: string | null
          start_date: string
          status?: Database["public"]["Enums"]["cycle_status"]
          term_count?: number | null
        }
        Update: {
          created_at?: string | null
          cycle_year?: number
          end_date?: string
          id?: string
          notes?: string | null
          start_date?: string
          status?: Database["public"]["Enums"]["cycle_status"]
          term_count?: number | null
        }
        Relationships: []
      }
      fellowship_impact_data: {
        Row: {
          absolute_improvement: number | null
          annual_avg: number | null
          annual_avg_percentage: number | null
          class_average_term_1: number | null
          class_average_term_2: number | null
          class_no: string | null
          class_size: number | null
          coach_average_improvement: number | null
          coach_name: string | null
          consistency_score: number | null
          created_at: string | null
          days_to_proficiency: number | null
          declining_from_passing: boolean | null
          deviation_from_class_term_1: number | null
          deviation_from_class_term_2: number | null
          deviation_from_grade_term_1: number | null
          deviation_from_grade_term_2: number | null
          deviation_from_subject_term_1: number | null
          deviation_from_subject_term_2: number | null
          excelling: boolean | null
          failed_both_terms: boolean | null
          fellow_name: string | null
          fellowship_year: string | null
          gap_to_excellence: number | null
          gap_to_passing: number | null
          grade: string | null
          grade_average_term_1: number | null
          grade_average_term_2: number | null
          growth_category: string | null
          has_both_terms: boolean | null
          has_term_1: boolean | null
          has_term_2: boolean | null
          id: number
          improved_to_excellence: boolean | null
          improved_to_proficiency: boolean | null
          improvement_letter_grade: string | null
          improvement_pct: number | null
          improvement_points: number | null
          is_at_risk_term_2: boolean | null
          is_decline: boolean | null
          is_excellent_term_2: boolean | null
          is_good_term_2: boolean | null
          is_high_growth: boolean | null
          is_moderate_growth: boolean | null
          is_satisfactory_term_2: boolean | null
          is_slight_growth: boolean | null
          is_stagnant: boolean | null
          moved_to_failing: boolean | null
          moved_to_passing: boolean | null
          needs_support: boolean | null
          needs_urgent_intervention: boolean | null
          on_track: boolean | null
          pass_term_1: boolean | null
          pass_term_2: boolean | null
          passed_both_terms: boolean | null
          percentile_improvement: number | null
          percentile_rank_term_1: number | null
          percentile_rank_term_2: number | null
          predicted_term_3: number | null
          reached_excellence: boolean | null
          reached_proficiency: boolean | null
          relative_to_coach_avg: number | null
          risk_score: number | null
          severely_declining: boolean | null
          sort_order: number | null
          stayed_failing: boolean | null
          stayed_passing: boolean | null
          subject: string | null
          subject_average_term_1: number | null
          subject_average_term_2: number | null
          success_probability: number | null
          term_1: number | null
          term_1_percentage: number | null
          term_2: number | null
          term_2_percentage: number | null
          updated_at: string | null
          volatility_score: number | null
          z_score_term_1: number | null
          z_score_term_2: number | null
        }
        Insert: {
          absolute_improvement?: number | null
          annual_avg?: number | null
          annual_avg_percentage?: number | null
          class_average_term_1?: number | null
          class_average_term_2?: number | null
          class_no?: string | null
          class_size?: number | null
          coach_average_improvement?: number | null
          coach_name?: string | null
          consistency_score?: number | null
          created_at?: string | null
          days_to_proficiency?: number | null
          declining_from_passing?: boolean | null
          deviation_from_class_term_1?: number | null
          deviation_from_class_term_2?: number | null
          deviation_from_grade_term_1?: number | null
          deviation_from_grade_term_2?: number | null
          deviation_from_subject_term_1?: number | null
          deviation_from_subject_term_2?: number | null
          excelling?: boolean | null
          failed_both_terms?: boolean | null
          fellow_name?: string | null
          fellowship_year?: string | null
          gap_to_excellence?: number | null
          gap_to_passing?: number | null
          grade?: string | null
          grade_average_term_1?: number | null
          grade_average_term_2?: number | null
          growth_category?: string | null
          has_both_terms?: boolean | null
          has_term_1?: boolean | null
          has_term_2?: boolean | null
          id?: number
          improved_to_excellence?: boolean | null
          improved_to_proficiency?: boolean | null
          improvement_letter_grade?: string | null
          improvement_pct?: number | null
          improvement_points?: number | null
          is_at_risk_term_2?: boolean | null
          is_decline?: boolean | null
          is_excellent_term_2?: boolean | null
          is_good_term_2?: boolean | null
          is_high_growth?: boolean | null
          is_moderate_growth?: boolean | null
          is_satisfactory_term_2?: boolean | null
          is_slight_growth?: boolean | null
          is_stagnant?: boolean | null
          moved_to_failing?: boolean | null
          moved_to_passing?: boolean | null
          needs_support?: boolean | null
          needs_urgent_intervention?: boolean | null
          on_track?: boolean | null
          pass_term_1?: boolean | null
          pass_term_2?: boolean | null
          passed_both_terms?: boolean | null
          percentile_improvement?: number | null
          percentile_rank_term_1?: number | null
          percentile_rank_term_2?: number | null
          predicted_term_3?: number | null
          reached_excellence?: boolean | null
          reached_proficiency?: boolean | null
          relative_to_coach_avg?: number | null
          risk_score?: number | null
          severely_declining?: boolean | null
          sort_order?: number | null
          stayed_failing?: boolean | null
          stayed_passing?: boolean | null
          subject?: string | null
          subject_average_term_1?: number | null
          subject_average_term_2?: number | null
          success_probability?: number | null
          term_1?: number | null
          term_1_percentage?: number | null
          term_2?: number | null
          term_2_percentage?: number | null
          updated_at?: string | null
          volatility_score?: number | null
          z_score_term_1?: number | null
          z_score_term_2?: number | null
        }
        Update: {
          absolute_improvement?: number | null
          annual_avg?: number | null
          annual_avg_percentage?: number | null
          class_average_term_1?: number | null
          class_average_term_2?: number | null
          class_no?: string | null
          class_size?: number | null
          coach_average_improvement?: number | null
          coach_name?: string | null
          consistency_score?: number | null
          created_at?: string | null
          days_to_proficiency?: number | null
          declining_from_passing?: boolean | null
          deviation_from_class_term_1?: number | null
          deviation_from_class_term_2?: number | null
          deviation_from_grade_term_1?: number | null
          deviation_from_grade_term_2?: number | null
          deviation_from_subject_term_1?: number | null
          deviation_from_subject_term_2?: number | null
          excelling?: boolean | null
          failed_both_terms?: boolean | null
          fellow_name?: string | null
          fellowship_year?: string | null
          gap_to_excellence?: number | null
          gap_to_passing?: number | null
          grade?: string | null
          grade_average_term_1?: number | null
          grade_average_term_2?: number | null
          growth_category?: string | null
          has_both_terms?: boolean | null
          has_term_1?: boolean | null
          has_term_2?: boolean | null
          id?: number
          improved_to_excellence?: boolean | null
          improved_to_proficiency?: boolean | null
          improvement_letter_grade?: string | null
          improvement_pct?: number | null
          improvement_points?: number | null
          is_at_risk_term_2?: boolean | null
          is_decline?: boolean | null
          is_excellent_term_2?: boolean | null
          is_good_term_2?: boolean | null
          is_high_growth?: boolean | null
          is_moderate_growth?: boolean | null
          is_satisfactory_term_2?: boolean | null
          is_slight_growth?: boolean | null
          is_stagnant?: boolean | null
          moved_to_failing?: boolean | null
          moved_to_passing?: boolean | null
          needs_support?: boolean | null
          needs_urgent_intervention?: boolean | null
          on_track?: boolean | null
          pass_term_1?: boolean | null
          pass_term_2?: boolean | null
          passed_both_terms?: boolean | null
          percentile_improvement?: number | null
          percentile_rank_term_1?: number | null
          percentile_rank_term_2?: number | null
          predicted_term_3?: number | null
          reached_excellence?: boolean | null
          reached_proficiency?: boolean | null
          relative_to_coach_avg?: number | null
          risk_score?: number | null
          severely_declining?: boolean | null
          sort_order?: number | null
          stayed_failing?: boolean | null
          stayed_passing?: boolean | null
          subject?: string | null
          subject_average_term_1?: number | null
          subject_average_term_2?: number | null
          success_probability?: number | null
          term_1?: number | null
          term_1_percentage?: number | null
          term_2?: number | null
          term_2_percentage?: number | null
          updated_at?: string | null
          volatility_score?: number | null
          z_score_term_1?: number | null
          z_score_term_2?: number | null
        }
        Relationships: []
      }
      fellowship_terms: {
        Row: {
          created_at: string | null
          data_collection_window: unknown | null
          end_date: string
          fellowship_cycle_id: string
          id: string
          is_active: boolean | null
          label: string
          start_date: string
          term_number: number
        }
        Insert: {
          created_at?: string | null
          data_collection_window?: unknown | null
          end_date: string
          fellowship_cycle_id: string
          id?: string
          is_active?: boolean | null
          label: string
          start_date: string
          term_number: number
        }
        Update: {
          created_at?: string | null
          data_collection_window?: unknown | null
          end_date?: string
          fellowship_cycle_id?: string
          id?: string
          is_active?: boolean | null
          label?: string
          start_date?: string
          term_number?: number
        }
        Relationships: [
          {
            foreignKeyName: "fellowship_terms_fellowship_cycle_id_fkey"
            columns: ["fellowship_cycle_id"]
            isOneToOne: false
            referencedRelation: "fellowship_cycles"
            referencedColumns: ["id"]
          },
        ]
      }
      flyway_schema_history: {
        Row: {
          checksum: number | null
          description: string
          execution_time: number
          installed_by: string
          installed_on: string
          installed_rank: number
          script: string
          success: boolean
          type: string
          version: string | null
        }
        Insert: {
          checksum?: number | null
          description: string
          execution_time: number
          installed_by: string
          installed_on?: string
          installed_rank: number
          script: string
          success: boolean
          type: string
          version?: string | null
        }
        Update: {
          checksum?: number | null
          description?: string
          execution_time?: number
          installed_by?: string
          installed_on?: string
          installed_rank?: number
          script?: string
          success?: boolean
          type?: string
          version?: string | null
        }
        Relationships: []
      }
      indicator_scores: {
        Row: {
          comment: string | null
          created_at: string | null
          indicator_id: string
          observation_id: string
          score: number | null
          score_id: string
        }
        Insert: {
          comment?: string | null
          created_at?: string | null
          indicator_id: string
          observation_id: string
          score?: number | null
          score_id?: string
        }
        Update: {
          comment?: string | null
          created_at?: string | null
          indicator_id?: string
          observation_id?: string
          score?: number | null
          score_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "indicator_scores_indicator_id_fkey"
            columns: ["indicator_id"]
            isOneToOne: false
            referencedRelation: "indicators"
            referencedColumns: ["indicator_id"]
          },
          {
            foreignKeyName: "indicator_scores_observation_id_fkey"
            columns: ["observation_id"]
            isOneToOne: false
            referencedRelation: "observations"
            referencedColumns: ["observation_id"]
          },
          {
            foreignKeyName: "indicator_scores_observation_id_fkey"
            columns: ["observation_id"]
            isOneToOne: false
            referencedRelation: "v_observation_full"
            referencedColumns: ["observation_id"]
          },
        ]
      }
      indicators: {
        Row: {
          domain_code: string
          indicator_id: string
          indicator_name: string | null
          question: string
          tier: string
        }
        Insert: {
          domain_code: string
          indicator_id: string
          indicator_name?: string | null
          question: string
          tier: string
        }
        Update: {
          domain_code?: string
          indicator_id?: string
          indicator_name?: string | null
          question?: string
          tier?: string
        }
        Relationships: [
          {
            foreignKeyName: "fk_domain"
            columns: ["domain_code"]
            isOneToOne: false
            referencedRelation: "domains"
            referencedColumns: ["domain_code"]
          },
        ]
      }
      modules: {
        Row: {
          created_at: string | null
          description: string | null
          id: string
          name: string
          nav_name: string
        }
        Insert: {
          created_at?: string | null
          description?: string | null
          id?: string
          name: string
          nav_name: string
        }
        Update: {
          created_at?: string | null
          description?: string | null
          id?: string
          name?: string
          nav_name?: string
        }
        Relationships: []
      }
      monthly_feedback: {
        Row: {
          coach: string
          created_at: string | null
          feedback: string
          id: string
          metric: string
          month: string
          term: string
          updated_at: string | null
        }
        Insert: {
          coach: string
          created_at?: string | null
          feedback: string
          id?: string
          metric: string
          month: string
          term: string
          updated_at?: string | null
        }
        Update: {
          coach?: string
          created_at?: string | null
          feedback?: string
          id?: string
          metric?: string
          month?: string
          term?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      observations: {
        Row: {
          class_size: number | null
          coach_name: string | null
          created_at: string | null
          date_lesson_observed: string | null
          fellow_name: string | null
          fellowship_year: number | null
          grade: string | null
          observation_id: string
          present_learners: number | null
          school_name: string | null
          subject: string | null
          term: string | null
          time_lesson: string | null
        }
        Insert: {
          class_size?: number | null
          coach_name?: string | null
          created_at?: string | null
          date_lesson_observed?: string | null
          fellow_name?: string | null
          fellowship_year?: number | null
          grade?: string | null
          observation_id?: string
          present_learners?: number | null
          school_name?: string | null
          subject?: string | null
          term?: string | null
          time_lesson?: string | null
        }
        Update: {
          class_size?: number | null
          coach_name?: string | null
          created_at?: string | null
          date_lesson_observed?: string | null
          fellow_name?: string | null
          fellowship_year?: number | null
          grade?: string | null
          observation_id?: string
          present_learners?: number | null
          school_name?: string | null
          subject?: string | null
          term?: string | null
          time_lesson?: string | null
        }
        Relationships: []
      }
      observations_stage_table: {
        Row: {
          __version__: string | null
          _id: number | null
          _index: number | null
          _notes: string | null
          _status: string | null
          _submission_time: string | null
          _submitted_by: string | null
          _tags: string[] | null
          _uuid: string
          _validation_status: string | null
          additional_comments: string | null
          areas_for_improvement: string | null
          class_size: number | null
          coach_name: string | null
          date_lesson_observed: string | null
          fellow_name: string | null
          fellowship_year: number | null
          grade: string | null
          next_steps: string | null
          overall_effectiveness: number | null
          present_learners: number | null
          q_aii_adjustments: number | null
          q_aii_differentiation: number | null
          q_aii_feedback: number | null
          q_aii_remediation: number | null
          q_ial_impact: number | null
          q_ial_practice: number | null
          q_ial_real_world: number | null
          q_ian_learner_ideas: number | null
          q_ian_models: number | null
          q_ian_questioning: number | null
          q_kpc_alignment: number | null
          q_kpc_background: number | null
          q_kpc_objective: number | null
          q_kpc_previous_learning: number | null
          q_kpc_problem_solving: number | null
          q_le_environment: number | null
          q_le_groupwork: number | null
          q_le_leadership: number | null
          q_le_learner_interactions: number | null
          q_le_rules: number | null
          q_le_teacher_interactions: number | null
          q_se_groupwork_plan: number | null
          q_se_practice_time: number | null
          q_se_understanding: number | null
          school_name: string | null
          strengths: string | null
          subject: string | null
          term: string | null
          time_lesson: string | null
        }
        Insert: {
          __version__?: string | null
          _id?: number | null
          _index?: number | null
          _notes?: string | null
          _status?: string | null
          _submission_time?: string | null
          _submitted_by?: string | null
          _tags?: string[] | null
          _uuid: string
          _validation_status?: string | null
          additional_comments?: string | null
          areas_for_improvement?: string | null
          class_size?: number | null
          coach_name?: string | null
          date_lesson_observed?: string | null
          fellow_name?: string | null
          fellowship_year?: number | null
          grade?: string | null
          next_steps?: string | null
          overall_effectiveness?: number | null
          present_learners?: number | null
          q_aii_adjustments?: number | null
          q_aii_differentiation?: number | null
          q_aii_feedback?: number | null
          q_aii_remediation?: number | null
          q_ial_impact?: number | null
          q_ial_practice?: number | null
          q_ial_real_world?: number | null
          q_ian_learner_ideas?: number | null
          q_ian_models?: number | null
          q_ian_questioning?: number | null
          q_kpc_alignment?: number | null
          q_kpc_background?: number | null
          q_kpc_objective?: number | null
          q_kpc_previous_learning?: number | null
          q_kpc_problem_solving?: number | null
          q_le_environment?: number | null
          q_le_groupwork?: number | null
          q_le_leadership?: number | null
          q_le_learner_interactions?: number | null
          q_le_rules?: number | null
          q_le_teacher_interactions?: number | null
          q_se_groupwork_plan?: number | null
          q_se_practice_time?: number | null
          q_se_understanding?: number | null
          school_name?: string | null
          strengths?: string | null
          subject?: string | null
          term?: string | null
          time_lesson?: string | null
        }
        Update: {
          __version__?: string | null
          _id?: number | null
          _index?: number | null
          _notes?: string | null
          _status?: string | null
          _submission_time?: string | null
          _submitted_by?: string | null
          _tags?: string[] | null
          _uuid?: string
          _validation_status?: string | null
          additional_comments?: string | null
          areas_for_improvement?: string | null
          class_size?: number | null
          coach_name?: string | null
          date_lesson_observed?: string | null
          fellow_name?: string | null
          fellowship_year?: number | null
          grade?: string | null
          next_steps?: string | null
          overall_effectiveness?: number | null
          present_learners?: number | null
          q_aii_adjustments?: number | null
          q_aii_differentiation?: number | null
          q_aii_feedback?: number | null
          q_aii_remediation?: number | null
          q_ial_impact?: number | null
          q_ial_practice?: number | null
          q_ial_real_world?: number | null
          q_ian_learner_ideas?: number | null
          q_ian_models?: number | null
          q_ian_questioning?: number | null
          q_kpc_alignment?: number | null
          q_kpc_background?: number | null
          q_kpc_objective?: number | null
          q_kpc_previous_learning?: number | null
          q_kpc_problem_solving?: number | null
          q_le_environment?: number | null
          q_le_groupwork?: number | null
          q_le_leadership?: number | null
          q_le_learner_interactions?: number | null
          q_le_rules?: number | null
          q_le_teacher_interactions?: number | null
          q_se_groupwork_plan?: number | null
          q_se_practice_time?: number | null
          q_se_understanding?: number | null
          school_name?: string | null
          strengths?: string | null
          subject?: string | null
          term?: string | null
          time_lesson?: string | null
        }
        Relationships: []
      }
      overall_feedback: {
        Row: {
          areas_needing_improvement: string | null
          areas_of_progress: string | null
          coach: string
          created_at: string | null
          date_submitted: string
          id: string
          metric: string | null
          notes: string | null
          recommendations: string | null
          term_reviewed: string
          updated_at: string | null
        }
        Insert: {
          areas_needing_improvement?: string | null
          areas_of_progress?: string | null
          coach: string
          created_at?: string | null
          date_submitted: string
          id?: string
          metric?: string | null
          notes?: string | null
          recommendations?: string | null
          term_reviewed: string
          updated_at?: string | null
        }
        Update: {
          areas_needing_improvement?: string | null
          areas_of_progress?: string | null
          coach?: string
          created_at?: string | null
          date_submitted?: string
          id?: string
          metric?: string | null
          notes?: string | null
          recommendations?: string | null
          term_reviewed?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      qualifications: {
        Row: {
          created_at: string | null
          fellow_id: string
          id: string
          institution: string
          level: string
          qualification_name: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          fellow_id: string
          id?: string
          institution: string
          level: string
          qualification_name: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          fellow_id?: string
          id?: string
          institution?: string
          level?: string
          qualification_name?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "qualifications_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "qualifications_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "qualifications_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellows"
            referencedColumns: ["id"]
          },
        ]
      }
      report_academic_results: {
        Row: {
          class_name: string | null
          class_no: string | null
          class_size: number | null
          coach_name: string
          created_at: string | null
          fellow_name: string
          fellowship_year: number
          fellowship_year_display: string | null
          grade: number | null
          grade_display: string | null
          id: string
          phase_display: string | null
          subject: string | null
          term_1_avg: number | null
          term_2_avg: number | null
          updated_at: string | null
        }
        Insert: {
          class_name?: string | null
          class_no?: string | null
          class_size?: number | null
          coach_name: string
          created_at?: string | null
          fellow_name: string
          fellowship_year: number
          fellowship_year_display?: string | null
          grade?: number | null
          grade_display?: string | null
          id?: string
          phase_display?: string | null
          subject?: string | null
          term_1_avg?: number | null
          term_2_avg?: number | null
          updated_at?: string | null
        }
        Update: {
          class_name?: string | null
          class_no?: string | null
          class_size?: number | null
          coach_name?: string
          created_at?: string | null
          fellow_name?: string
          fellowship_year?: number
          fellowship_year_display?: string | null
          grade?: number | null
          grade_display?: string | null
          id?: string
          phase_display?: string | null
          subject?: string | null
          term_1_avg?: number | null
          term_2_avg?: number | null
          updated_at?: string | null
        }
        Relationships: []
      }
      role_modules: {
        Row: {
          created_at: string | null
          id: string
          module_id: string
          role_id: string
        }
        Insert: {
          created_at?: string | null
          id?: string
          module_id: string
          role_id: string
        }
        Update: {
          created_at?: string | null
          id?: string
          module_id?: string
          role_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "role_modules_module_id_fkey"
            columns: ["module_id"]
            isOneToOne: false
            referencedRelation: "modules"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "role_modules_role_id_fkey"
            columns: ["role_id"]
            isOneToOne: false
            referencedRelation: "roles"
            referencedColumns: ["id"]
          },
        ]
      }
      roles: {
        Row: {
          access_level: string
          created_at: string | null
          description: string | null
          id: string
          name: string
        }
        Insert: {
          access_level: string
          created_at?: string | null
          description?: string | null
          id?: string
          name: string
        }
        Update: {
          access_level?: string
          created_at?: string | null
          description?: string | null
          id?: string
          name?: string
        }
        Relationships: []
      }
      school_assignments: {
        Row: {
          appointment_type: string | null
          assigned_by: string | null
          assignment_end: string | null
          assignment_start: string | null
          created_at: string
          fellow_id: string
          id: string
          is_active: boolean
          placed_by_ttn: string | null
          post_level: string | null
          post_type: string | null
          school_id: string
        }
        Insert: {
          appointment_type?: string | null
          assigned_by?: string | null
          assignment_end?: string | null
          assignment_start?: string | null
          created_at?: string
          fellow_id: string
          id?: string
          is_active?: boolean
          placed_by_ttn?: string | null
          post_level?: string | null
          post_type?: string | null
          school_id: string
        }
        Update: {
          appointment_type?: string | null
          assigned_by?: string | null
          assignment_end?: string | null
          assignment_start?: string | null
          created_at?: string
          fellow_id?: string
          id?: string
          is_active?: boolean
          placed_by_ttn?: string | null
          post_level?: string | null
          post_type?: string | null
          school_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "school_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "school_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "school_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellows"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "school_assignments_school_id_fkey"
            columns: ["school_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["school_id"]
          },
          {
            foreignKeyName: "school_assignments_school_id_fkey"
            columns: ["school_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["school_id"]
          },
          {
            foreignKeyName: "school_assignments_school_id_fkey"
            columns: ["school_id"]
            isOneToOne: false
            referencedRelation: "schools"
            referencedColumns: ["id"]
          },
        ]
      }
      school_corrections: {
        Row: {
          canonical_name: string
          corrected_phase: string
          id: string
          original_name: string
        }
        Insert: {
          canonical_name: string
          corrected_phase: string
          id?: string
          original_name: string
        }
        Update: {
          canonical_name?: string
          corrected_phase?: string
          id?: string
          original_name?: string
        }
        Relationships: []
      }
      school_placements: {
        Row: {
          created_at: string | null
          data_source: string | null
          fellow_id: string
          id: string
          placed_by_ttn: boolean | null
          school_id: string
          school_name: string
          teaching_status: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          data_source?: string | null
          fellow_id: string
          id?: string
          placed_by_ttn?: boolean | null
          school_id: string
          school_name: string
          teaching_status: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          data_source?: string | null
          fellow_id?: string
          id?: string
          placed_by_ttn?: boolean | null
          school_id?: string
          school_name?: string
          teaching_status?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "fk_school_placements_fellow"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_demographics"
            referencedColumns: ["id"]
          },
        ]
      }
      schools: {
        Row: {
          address: string | null
          created_at: string
          education_district: string | null
          id: string
          is_ecd: boolean | null
          is_fet_phase: boolean | null
          is_foundation_phase: boolean | null
          is_intermediate_phase: boolean | null
          is_primary: boolean | null
          is_secondary: boolean | null
          is_senior_phase: boolean | null
          name: string
          principal_contact: string | null
          principal_email: string | null
          principal_name: string | null
          province: string | null
          region: string | null
          school_contact: string | null
          school_email: string | null
          school_phase: string | null
          school_province: string | null
          stream: string | null
          suburb: string | null
          teaching_language: string | null
        }
        Insert: {
          address?: string | null
          created_at?: string
          education_district?: string | null
          id?: string
          is_ecd?: boolean | null
          is_fet_phase?: boolean | null
          is_foundation_phase?: boolean | null
          is_intermediate_phase?: boolean | null
          is_primary?: boolean | null
          is_secondary?: boolean | null
          is_senior_phase?: boolean | null
          name: string
          principal_contact?: string | null
          principal_email?: string | null
          principal_name?: string | null
          province?: string | null
          region?: string | null
          school_contact?: string | null
          school_email?: string | null
          school_phase?: string | null
          school_province?: string | null
          stream?: string | null
          suburb?: string | null
          teaching_language?: string | null
        }
        Update: {
          address?: string | null
          created_at?: string
          education_district?: string | null
          id?: string
          is_ecd?: boolean | null
          is_fet_phase?: boolean | null
          is_foundation_phase?: boolean | null
          is_intermediate_phase?: boolean | null
          is_primary?: boolean | null
          is_secondary?: boolean | null
          is_senior_phase?: boolean | null
          name?: string
          principal_contact?: string | null
          principal_email?: string | null
          principal_name?: string | null
          province?: string | null
          region?: string | null
          school_contact?: string | null
          school_email?: string | null
          school_phase?: string | null
          school_province?: string | null
          stream?: string | null
          suburb?: string | null
          teaching_language?: string | null
        }
        Relationships: []
      }
      schools_dev: {
        Row: {
          address: string | null
          educationDistrict: string | null
          id: string
          name: string
          principalContactNumber: string | null
          principalEmail: string | null
          principalName: string | null
          province: string | null
          quintileCategory: string | null
          region: string | null
          suburb: string | null
          type: string | null
        }
        Insert: {
          address?: string | null
          educationDistrict?: string | null
          id?: string
          name: string
          principalContactNumber?: string | null
          principalEmail?: string | null
          principalName?: string | null
          province?: string | null
          quintileCategory?: string | null
          region?: string | null
          suburb?: string | null
          type?: string | null
        }
        Update: {
          address?: string | null
          educationDistrict?: string | null
          id?: string
          name?: string
          principalContactNumber?: string | null
          principalEmail?: string | null
          principalName?: string | null
          province?: string | null
          quintileCategory?: string | null
          region?: string | null
          suburb?: string | null
          type?: string | null
        }
        Relationships: []
      }
      schools_main: {
        Row: {
          address: string | null
          created_at: string | null
          education_district: string | null
          id: string
          phase: string
          principal_contact: string | null
          principal_email: string | null
          principal_name: string | null
          province: string | null
          quantile: string | null
          region: string | null
          school_name: string
          suburb: string | null
          updated_at: string | null
        }
        Insert: {
          address?: string | null
          created_at?: string | null
          education_district?: string | null
          id?: string
          phase: string
          principal_contact?: string | null
          principal_email?: string | null
          principal_name?: string | null
          province?: string | null
          quantile?: string | null
          region?: string | null
          school_name: string
          suburb?: string | null
          updated_at?: string | null
        }
        Update: {
          address?: string | null
          created_at?: string | null
          education_district?: string | null
          id?: string
          phase?: string
          principal_contact?: string | null
          principal_email?: string | null
          principal_name?: string | null
          province?: string | null
          quantile?: string | null
          region?: string | null
          school_name?: string
          suburb?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      subject_assignments: {
        Row: {
          annual_avg: number | null
          class_assignment_id: string
          created_at: string | null
          fellow_id: string
          id: string
          learners: number
          subject: string
          t1: number | null
          t2: number | null
          t3: number | null
          t4: number | null
        }
        Insert: {
          annual_avg?: number | null
          class_assignment_id: string
          created_at?: string | null
          fellow_id: string
          id?: string
          learners: number
          subject: string
          t1?: number | null
          t2?: number | null
          t3?: number | null
          t4?: number | null
        }
        Update: {
          annual_avg?: number | null
          class_assignment_id?: string
          created_at?: string | null
          fellow_id?: string
          id?: string
          learners?: number
          subject?: string
          t1?: number | null
          t2?: number | null
          t3?: number | null
          t4?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "subject_assignments_class_assignment_id_fkey"
            columns: ["class_assignment_id"]
            isOneToOne: false
            referencedRelation: "class_assignments"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "subject_assignments_class_assignment_id_fkey"
            columns: ["class_assignment_id"]
            isOneToOne: false
            referencedRelation: "v_class_assignment_marks"
            referencedColumns: ["class_assignment_id"]
          },
          {
            foreignKeyName: "subject_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "subject_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "subject_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellows"
            referencedColumns: ["id"]
          },
        ]
      }
      subjects: {
        Row: {
          afrikaans_display_name: string | null
          category: string
          created_at: string | null
          id: string
          is_fet_phase: boolean | null
          is_foundation_phase: boolean | null
          is_intermediate_phase: boolean | null
          is_senior_phase: boolean | null
          language_level: string | null
          name: string
          short_code: string | null
          teaching_language: string
          updated_at: string | null
        }
        Insert: {
          afrikaans_display_name?: string | null
          category: string
          created_at?: string | null
          id?: string
          is_fet_phase?: boolean | null
          is_foundation_phase?: boolean | null
          is_intermediate_phase?: boolean | null
          is_senior_phase?: boolean | null
          language_level?: string | null
          name: string
          short_code?: string | null
          teaching_language?: string
          updated_at?: string | null
        }
        Update: {
          afrikaans_display_name?: string | null
          category?: string
          created_at?: string | null
          id?: string
          is_fet_phase?: boolean | null
          is_foundation_phase?: boolean | null
          is_intermediate_phase?: boolean | null
          is_senior_phase?: boolean | null
          language_level?: string | null
          name?: string
          short_code?: string | null
          teaching_language?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      successful_candidates: {
        Row: {
          acceptance_confirmation_received_date: string | null
          acceptance_letter_sent_by: string | null
          acceptance_letter_sent_date: string | null
          added_to_cohort_whatsapp_date: string | null
          added_to_placement_whatsapp: boolean | null
          age: number | null
          amount_funded_to_date: number | null
          assigned_recruitment_officer: string | null
          bed_pgce_qualification_received: boolean | null
          books_received: boolean | null
          category: string | null
          cellphone: string | null
          coach: string | null
          coach_informed_profile_complete: boolean | null
          cohort: string | null
          comments: string | null
          created_at: string | null
          date_of_birth: string | null
          documents_uploaded: boolean | null
          education_district: string | null
          email: string | null
          fellow_confirmation_email_date: string | null
          fellow_profile_priority: string | null
          fellow_profile_status: string | null
          fellowship_agreement_email_date: string | null
          fellowship_agreement_email_sent_by: string | null
          fellowship_agreement_signed: string | null
          fixed_term_contract_post: boolean | null
          full_time_permanent_post: boolean | null
          gender: string | null
          grade_teaching_subjects: string | null
          graduate_placement_status: string | null
          has_arts: boolean | null
          has_bed_pgce: boolean | null
          has_commerce: boolean | null
          has_foundation_phase: boolean | null
          has_languages: boolean | null
          has_stem_coding_robotics: boolean | null
          has_stemac: boolean | null
          id: string
          id_number: string | null
          interview_date: string | null
          interview_readiness_training_completed: boolean | null
          interview_type: string | null
          interviewer_feedback_sheet_completed: boolean | null
          interviewers: string | null
          mbti_personality_type: string | null
          media_consent_form_signed_date: string | null
          name: string | null
          onboarding_completion_percentage: number | null
          outstanding_documents: string | null
          outstanding_onboarding_docs: string | null
          overall_selection_score: number | null
          partnered_to: string | null
          pgce_agreement_signed: boolean | null
          pgce_bed_institution: string | null
          pgce_funded_by_ttn: boolean | null
          pgce_institution: string | null
          pgce_registered: boolean | null
          photo_cv_filed: boolean | null
          placed_by_ttn: boolean | null
          police_clearance_received: boolean | null
          postgraduate_qualification_institution: string | null
          principal_contact_number: string | null
          principal_email: string | null
          principal_name: string | null
          profile_checked_by_fellow: boolean | null
          profile_emailed_date: string | null
          profile_emailed_to_fellow_date: string | null
          profile_filed_in_folder: boolean | null
          profile_loaded_on_shortlisted: boolean | null
          proof_of_sars_registration: boolean | null
          province_of_origin: string | null
          race: string | null
          recruitment_welcome_video_sent: boolean | null
          sace_certificate_received: boolean | null
          sace_registration_no: string | null
          school_address: string | null
          school_province: string | null
          school_quintile_category: string | null
          school_region: string | null
          school_suburb: string | null
          school_type: string | null
          student_id_received: boolean | null
          teaching_experience_years: string | null
          teaching_phase: string | null
          teaching_status: string | null
          term1_program_dates_letter_date: string | null
          term1_program_dates_letter_sent_by: string | null
          ttn_contact: string | null
          undergrad_qualification_received: boolean | null
          undergraduate_degree_institution: string | null
          updated_at: string | null
          wced_vacancies_shared: boolean | null
          year_of_entry: number | null
          year_of_fellowship: number | null
        }
        Insert: {
          acceptance_confirmation_received_date?: string | null
          acceptance_letter_sent_by?: string | null
          acceptance_letter_sent_date?: string | null
          added_to_cohort_whatsapp_date?: string | null
          added_to_placement_whatsapp?: boolean | null
          age?: number | null
          amount_funded_to_date?: number | null
          assigned_recruitment_officer?: string | null
          bed_pgce_qualification_received?: boolean | null
          books_received?: boolean | null
          category?: string | null
          cellphone?: string | null
          coach?: string | null
          coach_informed_profile_complete?: boolean | null
          cohort?: string | null
          comments?: string | null
          created_at?: string | null
          date_of_birth?: string | null
          documents_uploaded?: boolean | null
          education_district?: string | null
          email?: string | null
          fellow_confirmation_email_date?: string | null
          fellow_profile_priority?: string | null
          fellow_profile_status?: string | null
          fellowship_agreement_email_date?: string | null
          fellowship_agreement_email_sent_by?: string | null
          fellowship_agreement_signed?: string | null
          fixed_term_contract_post?: boolean | null
          full_time_permanent_post?: boolean | null
          gender?: string | null
          grade_teaching_subjects?: string | null
          graduate_placement_status?: string | null
          has_arts?: boolean | null
          has_bed_pgce?: boolean | null
          has_commerce?: boolean | null
          has_foundation_phase?: boolean | null
          has_languages?: boolean | null
          has_stem_coding_robotics?: boolean | null
          has_stemac?: boolean | null
          id?: string
          id_number?: string | null
          interview_date?: string | null
          interview_readiness_training_completed?: boolean | null
          interview_type?: string | null
          interviewer_feedback_sheet_completed?: boolean | null
          interviewers?: string | null
          mbti_personality_type?: string | null
          media_consent_form_signed_date?: string | null
          name?: string | null
          onboarding_completion_percentage?: number | null
          outstanding_documents?: string | null
          outstanding_onboarding_docs?: string | null
          overall_selection_score?: number | null
          partnered_to?: string | null
          pgce_agreement_signed?: boolean | null
          pgce_bed_institution?: string | null
          pgce_funded_by_ttn?: boolean | null
          pgce_institution?: string | null
          pgce_registered?: boolean | null
          photo_cv_filed?: boolean | null
          placed_by_ttn?: boolean | null
          police_clearance_received?: boolean | null
          postgraduate_qualification_institution?: string | null
          principal_contact_number?: string | null
          principal_email?: string | null
          principal_name?: string | null
          profile_checked_by_fellow?: boolean | null
          profile_emailed_date?: string | null
          profile_emailed_to_fellow_date?: string | null
          profile_filed_in_folder?: boolean | null
          profile_loaded_on_shortlisted?: boolean | null
          proof_of_sars_registration?: boolean | null
          province_of_origin?: string | null
          race?: string | null
          recruitment_welcome_video_sent?: boolean | null
          sace_certificate_received?: boolean | null
          sace_registration_no?: string | null
          school_address?: string | null
          school_province?: string | null
          school_quintile_category?: string | null
          school_region?: string | null
          school_suburb?: string | null
          school_type?: string | null
          student_id_received?: boolean | null
          teaching_experience_years?: string | null
          teaching_phase?: string | null
          teaching_status?: string | null
          term1_program_dates_letter_date?: string | null
          term1_program_dates_letter_sent_by?: string | null
          ttn_contact?: string | null
          undergrad_qualification_received?: boolean | null
          undergraduate_degree_institution?: string | null
          updated_at?: string | null
          wced_vacancies_shared?: boolean | null
          year_of_entry?: number | null
          year_of_fellowship?: number | null
        }
        Update: {
          acceptance_confirmation_received_date?: string | null
          acceptance_letter_sent_by?: string | null
          acceptance_letter_sent_date?: string | null
          added_to_cohort_whatsapp_date?: string | null
          added_to_placement_whatsapp?: boolean | null
          age?: number | null
          amount_funded_to_date?: number | null
          assigned_recruitment_officer?: string | null
          bed_pgce_qualification_received?: boolean | null
          books_received?: boolean | null
          category?: string | null
          cellphone?: string | null
          coach?: string | null
          coach_informed_profile_complete?: boolean | null
          cohort?: string | null
          comments?: string | null
          created_at?: string | null
          date_of_birth?: string | null
          documents_uploaded?: boolean | null
          education_district?: string | null
          email?: string | null
          fellow_confirmation_email_date?: string | null
          fellow_profile_priority?: string | null
          fellow_profile_status?: string | null
          fellowship_agreement_email_date?: string | null
          fellowship_agreement_email_sent_by?: string | null
          fellowship_agreement_signed?: string | null
          fixed_term_contract_post?: boolean | null
          full_time_permanent_post?: boolean | null
          gender?: string | null
          grade_teaching_subjects?: string | null
          graduate_placement_status?: string | null
          has_arts?: boolean | null
          has_bed_pgce?: boolean | null
          has_commerce?: boolean | null
          has_foundation_phase?: boolean | null
          has_languages?: boolean | null
          has_stem_coding_robotics?: boolean | null
          has_stemac?: boolean | null
          id?: string
          id_number?: string | null
          interview_date?: string | null
          interview_readiness_training_completed?: boolean | null
          interview_type?: string | null
          interviewer_feedback_sheet_completed?: boolean | null
          interviewers?: string | null
          mbti_personality_type?: string | null
          media_consent_form_signed_date?: string | null
          name?: string | null
          onboarding_completion_percentage?: number | null
          outstanding_documents?: string | null
          outstanding_onboarding_docs?: string | null
          overall_selection_score?: number | null
          partnered_to?: string | null
          pgce_agreement_signed?: boolean | null
          pgce_bed_institution?: string | null
          pgce_funded_by_ttn?: boolean | null
          pgce_institution?: string | null
          pgce_registered?: boolean | null
          photo_cv_filed?: boolean | null
          placed_by_ttn?: boolean | null
          police_clearance_received?: boolean | null
          postgraduate_qualification_institution?: string | null
          principal_contact_number?: string | null
          principal_email?: string | null
          principal_name?: string | null
          profile_checked_by_fellow?: boolean | null
          profile_emailed_date?: string | null
          profile_emailed_to_fellow_date?: string | null
          profile_filed_in_folder?: boolean | null
          profile_loaded_on_shortlisted?: boolean | null
          proof_of_sars_registration?: boolean | null
          province_of_origin?: string | null
          race?: string | null
          recruitment_welcome_video_sent?: boolean | null
          sace_certificate_received?: boolean | null
          sace_registration_no?: string | null
          school_address?: string | null
          school_province?: string | null
          school_quintile_category?: string | null
          school_region?: string | null
          school_suburb?: string | null
          school_type?: string | null
          student_id_received?: boolean | null
          teaching_experience_years?: string | null
          teaching_phase?: string | null
          teaching_status?: string | null
          term1_program_dates_letter_date?: string | null
          term1_program_dates_letter_sent_by?: string | null
          ttn_contact?: string | null
          undergrad_qualification_received?: boolean | null
          undergraduate_degree_institution?: string | null
          updated_at?: string | null
          wced_vacancies_shared?: boolean | null
          year_of_entry?: number | null
          year_of_fellowship?: number | null
        }
        Relationships: []
      }
      teacher_wellbeing: {
        Row: {
          ability_to_deal_with_stress: number | null
          ability_to_solve_problems_and_conflict: number | null
          access_to_credit_facilities: number | null
          access_to_health_care: number | null
          advice_and_mentorship: number | null
          alignment_of_personal_and_school_values: number | null
          aspiration: number | null
          authenticity_able_to_be_myself_at_school: number | null
          autonomy_as_professional_teacher: number | null
          budgeting_and_planning: number | null
          caring_and_loving_relationships: number | null
          category: string | null
          co_curricular_activities: number | null
          coach: string | null
          common_vision_and_mission: number | null
          conviction_about_choice_of_career: number | null
          creative_freedom_to_accomplish_work: number | null
          date: string | null
          date_of_survey: string | null
          deep_engagement_in_teaching_process: number | null
          distance_and_time_to_work: number | null
          doing_well: number | null
          drugs_and_alcohol: number | null
          educational_opportunities: number | null
          effective_communication: number | null
          electricity: number | null
          employment_contract: number | null
          family_unity: number | null
          feedback_on_performance: number | null
          fellow: string | null
          fulfilment_derived_from_work: number | null
          home_and_community_security: number | null
          house_structure: number | null
          id: number
          identity_card: string | null
          income_and_earnings_to_meet_needs: number | null
          influence_on_classroom_culture: number | null
          influence_on_colleagues_and_school_culture: number | null
          joy_in_teaching: number | null
          latitude: number | null
          longitude: number | null
          management_of_debt: number | null
          motivated: number | null
          nutrition: number | null
          open_communication_on_non_school_topics: number | null
          pedagogy_for_effective_performance: number | null
          perceived_value_in_society_as_teacher: number | null
          personal_savings: number | null
          physical_health_and_personal_hygiene: number | null
          pride_in_work: number | null
          proactive_teaching_approaches: number | null
          regular_means_of_transportation: number | null
          remuneration_aligned_with_responsibilities: number | null
          reputation_with_colleagues_and_learners: number | null
          respect_and_being_valued: number | null
          role_model_at_school: number | null
          sanitation_and_sewage: number | null
          self_awareness: number | null
          self_confidence: number | null
          self_esteem_and_trust: number | null
          sense_of_belonging_inclusion: number | null
          sense_of_confidence_in_management: number | null
          sense_of_control: number | null
          sensitivity_to_different_socio_economic_backgrounds: number | null
          separate_sleeping_spaces: number | null
          sleep: number | null
          social_networks: number | null
          stimulating_sense_of_purpose_in_learners: number | null
          stove_fridge_and_kitchen: number | null
          stuck: number | null
          sub_category: string | null
          support_for_professional_development: number | null
          supportive_relationships_with_colleagues: number | null
          survey_timeline: string | null
          term: string | null
          thriving: number | null
          trying_but_struggling: number | null
          workload: number | null
        }
        Insert: {
          ability_to_deal_with_stress?: number | null
          ability_to_solve_problems_and_conflict?: number | null
          access_to_credit_facilities?: number | null
          access_to_health_care?: number | null
          advice_and_mentorship?: number | null
          alignment_of_personal_and_school_values?: number | null
          aspiration?: number | null
          authenticity_able_to_be_myself_at_school?: number | null
          autonomy_as_professional_teacher?: number | null
          budgeting_and_planning?: number | null
          caring_and_loving_relationships?: number | null
          category?: string | null
          co_curricular_activities?: number | null
          coach?: string | null
          common_vision_and_mission?: number | null
          conviction_about_choice_of_career?: number | null
          creative_freedom_to_accomplish_work?: number | null
          date?: string | null
          date_of_survey?: string | null
          deep_engagement_in_teaching_process?: number | null
          distance_and_time_to_work?: number | null
          doing_well?: number | null
          drugs_and_alcohol?: number | null
          educational_opportunities?: number | null
          effective_communication?: number | null
          electricity?: number | null
          employment_contract?: number | null
          family_unity?: number | null
          feedback_on_performance?: number | null
          fellow?: string | null
          fulfilment_derived_from_work?: number | null
          home_and_community_security?: number | null
          house_structure?: number | null
          id?: number
          identity_card?: string | null
          income_and_earnings_to_meet_needs?: number | null
          influence_on_classroom_culture?: number | null
          influence_on_colleagues_and_school_culture?: number | null
          joy_in_teaching?: number | null
          latitude?: number | null
          longitude?: number | null
          management_of_debt?: number | null
          motivated?: number | null
          nutrition?: number | null
          open_communication_on_non_school_topics?: number | null
          pedagogy_for_effective_performance?: number | null
          perceived_value_in_society_as_teacher?: number | null
          personal_savings?: number | null
          physical_health_and_personal_hygiene?: number | null
          pride_in_work?: number | null
          proactive_teaching_approaches?: number | null
          regular_means_of_transportation?: number | null
          remuneration_aligned_with_responsibilities?: number | null
          reputation_with_colleagues_and_learners?: number | null
          respect_and_being_valued?: number | null
          role_model_at_school?: number | null
          sanitation_and_sewage?: number | null
          self_awareness?: number | null
          self_confidence?: number | null
          self_esteem_and_trust?: number | null
          sense_of_belonging_inclusion?: number | null
          sense_of_confidence_in_management?: number | null
          sense_of_control?: number | null
          sensitivity_to_different_socio_economic_backgrounds?: number | null
          separate_sleeping_spaces?: number | null
          sleep?: number | null
          social_networks?: number | null
          stimulating_sense_of_purpose_in_learners?: number | null
          stove_fridge_and_kitchen?: number | null
          stuck?: number | null
          sub_category?: string | null
          support_for_professional_development?: number | null
          supportive_relationships_with_colleagues?: number | null
          survey_timeline?: string | null
          term?: string | null
          thriving?: number | null
          trying_but_struggling?: number | null
          workload?: number | null
        }
        Update: {
          ability_to_deal_with_stress?: number | null
          ability_to_solve_problems_and_conflict?: number | null
          access_to_credit_facilities?: number | null
          access_to_health_care?: number | null
          advice_and_mentorship?: number | null
          alignment_of_personal_and_school_values?: number | null
          aspiration?: number | null
          authenticity_able_to_be_myself_at_school?: number | null
          autonomy_as_professional_teacher?: number | null
          budgeting_and_planning?: number | null
          caring_and_loving_relationships?: number | null
          category?: string | null
          co_curricular_activities?: number | null
          coach?: string | null
          common_vision_and_mission?: number | null
          conviction_about_choice_of_career?: number | null
          creative_freedom_to_accomplish_work?: number | null
          date?: string | null
          date_of_survey?: string | null
          deep_engagement_in_teaching_process?: number | null
          distance_and_time_to_work?: number | null
          doing_well?: number | null
          drugs_and_alcohol?: number | null
          educational_opportunities?: number | null
          effective_communication?: number | null
          electricity?: number | null
          employment_contract?: number | null
          family_unity?: number | null
          feedback_on_performance?: number | null
          fellow?: string | null
          fulfilment_derived_from_work?: number | null
          home_and_community_security?: number | null
          house_structure?: number | null
          id?: number
          identity_card?: string | null
          income_and_earnings_to_meet_needs?: number | null
          influence_on_classroom_culture?: number | null
          influence_on_colleagues_and_school_culture?: number | null
          joy_in_teaching?: number | null
          latitude?: number | null
          longitude?: number | null
          management_of_debt?: number | null
          motivated?: number | null
          nutrition?: number | null
          open_communication_on_non_school_topics?: number | null
          pedagogy_for_effective_performance?: number | null
          perceived_value_in_society_as_teacher?: number | null
          personal_savings?: number | null
          physical_health_and_personal_hygiene?: number | null
          pride_in_work?: number | null
          proactive_teaching_approaches?: number | null
          regular_means_of_transportation?: number | null
          remuneration_aligned_with_responsibilities?: number | null
          reputation_with_colleagues_and_learners?: number | null
          respect_and_being_valued?: number | null
          role_model_at_school?: number | null
          sanitation_and_sewage?: number | null
          self_awareness?: number | null
          self_confidence?: number | null
          self_esteem_and_trust?: number | null
          sense_of_belonging_inclusion?: number | null
          sense_of_confidence_in_management?: number | null
          sense_of_control?: number | null
          sensitivity_to_different_socio_economic_backgrounds?: number | null
          separate_sleeping_spaces?: number | null
          sleep?: number | null
          social_networks?: number | null
          stimulating_sense_of_purpose_in_learners?: number | null
          stove_fridge_and_kitchen?: number | null
          stuck?: number | null
          sub_category?: string | null
          support_for_professional_development?: number | null
          supportive_relationships_with_colleagues?: number | null
          survey_timeline?: string | null
          term?: string | null
          thriving?: number | null
          trying_but_struggling?: number | null
          workload?: number | null
        }
        Relationships: []
      }
      teaching_assignments: {
        Row: {
          created_at: string | null
          fellow_id: string
          grades: string[]
          id: string
          school_phase: string | null
          subjects: string[]
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          fellow_id: string
          grades: string[]
          id?: string
          school_phase?: string | null
          subjects: string[]
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          fellow_id?: string
          grades?: string[]
          id?: string
          school_phase?: string | null
          subjects?: string[]
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "teaching_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "teaching_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "teaching_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellows"
            referencedColumns: ["id"]
          },
        ]
      }
      teaching_qualifications: {
        Row: {
          created_at: string | null
          fellow_id: string | null
          id: string
          institution: string
          phase_specialisations: string[]
          qualification_type: string
          subject_specialisations: string[]
        }
        Insert: {
          created_at?: string | null
          fellow_id?: string | null
          id?: string
          institution: string
          phase_specialisations: string[]
          qualification_type: string
          subject_specialisations: string[]
        }
        Update: {
          created_at?: string | null
          fellow_id?: string | null
          id?: string
          institution?: string
          phase_specialisations?: string[]
          qualification_type?: string
          subject_specialisations?: string[]
        }
        Relationships: [
          {
            foreignKeyName: "teaching_qualifications_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "teaching_qualifications_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "teaching_qualifications_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellows"
            referencedColumns: ["id"]
          },
        ]
      }
      teaching_subjects: {
        Row: {
          class_id: string
          created_at: string | null
          id: string
          subject: string
          term_1_mark: number | null
          term_2_mark: number | null
          updated_at: string | null
        }
        Insert: {
          class_id: string
          created_at?: string | null
          id?: string
          subject: string
          term_1_mark?: number | null
          term_2_mark?: number | null
          updated_at?: string | null
        }
        Update: {
          class_id?: string
          created_at?: string | null
          id?: string
          subject?: string
          term_1_mark?: number | null
          term_2_mark?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "teaching_subjects_class_id_fkey"
            columns: ["class_id"]
            isOneToOne: false
            referencedRelation: "classes"
            referencedColumns: ["id"]
          },
        ]
      }
      user_profiles: {
        Row: {
          created_at: string | null
          email: string
          first_name: string | null
          id: string
          is_complete: boolean
          last_name: string | null
          phone: string | null
          primary_role_id: string
          updated_at: string | null
          user_id: string
          user_type: string
        }
        Insert: {
          created_at?: string | null
          email: string
          first_name?: string | null
          id?: string
          is_complete?: boolean
          last_name?: string | null
          phone?: string | null
          primary_role_id: string
          updated_at?: string | null
          user_id: string
          user_type: string
        }
        Update: {
          created_at?: string | null
          email?: string
          first_name?: string | null
          id?: string
          is_complete?: boolean
          last_name?: string | null
          phone?: string | null
          primary_role_id?: string
          updated_at?: string | null
          user_id?: string
          user_type?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_profiles_primary_role_id_fkey"
            columns: ["primary_role_id"]
            isOneToOne: false
            referencedRelation: "roles"
            referencedColumns: ["id"]
          },
        ]
      }
      user_roles: {
        Row: {
          created_at: string | null
          id: string
          role_id: string
          user_id: string
        }
        Insert: {
          created_at?: string | null
          id?: string
          role_id: string
          user_id: string
        }
        Update: {
          created_at?: string | null
          id?: string
          role_id?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_roles_role_id_fkey"
            columns: ["role_id"]
            isOneToOne: false
            referencedRelation: "roles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_roles_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "user_profiles"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      cohort_comparison_summary: {
        Row: {
          avg_classes_per_fellow: number | null
          classes_in_analysis: number | null
          cohort_number: number | null
          fellows_in_analysis: number | null
          pct_fellows_included: number | null
          total_fellows_in_cohort: number | null
          year_of_fellowship: number | null
        }
        Relationships: []
      }
      data_quality_summary: {
        Row: {
          category: string | null
          exclusion_reason: string | null
          percentage: number | null
          total_records: number | null
          unique_fellows: number | null
        }
        Relationships: []
      }
      fellow_profile: {
        Row: {
          appointment_type: string | null
          cellphone: string | null
          coach_assignment_id: string | null
          coach_email: string | null
          coach_id: string | null
          coach_name: string | null
          coach_type: string | null
          cohort_name: string | null
          email: string | null
          fellow_id: string | null
          full_name: string | null
          gender: string | null
          partner_organization: string | null
          placed_by_ttn: string | null
          post_level: string | null
          post_type: string | null
          race: string | null
          school_assignment_id: string | null
          school_id: string | null
          school_name: string | null
          school_phase: string | null
          school_province: string | null
          status: string | null
          year_of_fellowship: number | null
        }
        Relationships: []
      }
      fellow_profile_live: {
        Row: {
          appointment_type: string | null
          cellphone: string | null
          coach_assignment_id: string | null
          coach_email: string | null
          coach_id: string | null
          coach_name: string | null
          coach_type: string | null
          cohort_name: string | null
          email: string | null
          fellow_id: string | null
          full_name: string | null
          gender: string | null
          partner_organization: string | null
          placed_by_ttn: string | null
          post_level: string | null
          post_type: string | null
          race: string | null
          school_assignment_id: string | null
          school_id: string | null
          school_name: string | null
          school_phase: string | null
          school_province: string | null
          status: string | null
          year_of_fellowship: number | null
        }
        Relationships: []
      }
      missing_data_patterns: {
        Row: {
          classes_missing_term1: number | null
          fellows_affected: number | null
          pct_of_missing_data: number | null
          phase_cleaned: string | null
          subject_category_cleaned: string | null
        }
        Relationships: []
      }
      v_class_assignment_marks: {
        Row: {
          annual_avg: number | null
          class_assignment_id: string | null
          class_size: number | null
          fellow_id: string | null
          grade: number | null
          learners: number | null
          phase: string | null
          school_assignment_id: string | null
          t1_avg: number | null
          t2_avg: number | null
          t3_avg: number | null
          t4_avg: number | null
        }
        Relationships: [
          {
            foreignKeyName: "class_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "class_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "class_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellows"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "class_assignments_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["school_assignment_id"]
          },
          {
            foreignKeyName: "class_assignments_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["school_assignment_id"]
          },
          {
            foreignKeyName: "class_assignments_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "school_assignments"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "class_assignments_school_assignment_id_fkey"
            columns: ["school_assignment_id"]
            isOneToOne: false
            referencedRelation: "vw_school_assignments"
            referencedColumns: ["assignment_id"]
          },
        ]
      }
      v_observation_full: {
        Row: {
          additional_comments: string | null
          areas_for_improvement: string | null
          class_size: number | null
          classification: string | null
          coach_name: string | null
          date_lesson_observed: string | null
          domain: string | null
          domain_avg: number | null
          feedback_created_at: string | null
          feedback_id: string | null
          fellow_name: string | null
          fellowship_year: number | null
          grade: string | null
          next_steps: string | null
          observation_created_at: string | null
          observation_id: string | null
          overall_effectiveness: number | null
          present_learners: number | null
          school_name: string | null
          strengths: string | null
          strongest_tier: string | null
          subject: string | null
          term: string | null
          tier1_score: number | null
          tier2_score: number | null
          tier3_score: number | null
          time_lesson: string | null
          weakest_tier: string | null
        }
        Relationships: []
      }
      vw_school_assignments: {
        Row: {
          appointment_type: string | null
          assignment_end: string | null
          assignment_id: string | null
          assignment_start: string | null
          cohort_name: string | null
          created_at: string | null
          date_of_birth: string | null
          fellow_id: string | null
          fellow_name: string | null
          fellow_status: string | null
          gender: string | null
          is_active: boolean | null
          placed_by_ttn: string | null
          post_level: string | null
          post_type: string | null
          province_of_origin: string | null
          race: string | null
          school_id: string | null
          school_name: string | null
          school_phase: string | null
          school_province: string | null
          school_province_alt: string | null
          school_stream: string | null
          teaching_language: string | null
          year_of_entry: string | null
          year_of_fellowship: number | null
        }
        Relationships: [
          {
            foreignKeyName: "school_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "school_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["fellow_id"]
          },
          {
            foreignKeyName: "school_assignments_fellow_id_fkey"
            columns: ["fellow_id"]
            isOneToOne: false
            referencedRelation: "fellows"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "school_assignments_school_id_fkey"
            columns: ["school_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile"
            referencedColumns: ["school_id"]
          },
          {
            foreignKeyName: "school_assignments_school_id_fkey"
            columns: ["school_id"]
            isOneToOne: false
            referencedRelation: "fellow_profile_live"
            referencedColumns: ["school_id"]
          },
          {
            foreignKeyName: "school_assignments_school_id_fkey"
            columns: ["school_id"]
            isOneToOne: false
            referencedRelation: "schools"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      assignments_assignmenttype_enum: "CoachDev" | "SchoolDev" | "Other"
      cycle_status: "draft" | "active" | "locked" | "archived"
      fellows_dev_phasespecialization_enum:
        | "Foundation"
        | "Intermediate"
        | "Senior"
        | "FET"
      fellows_dev_qualificationtype_enum: "BEd" | "PGCE"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {
      assignments_assignmenttype_enum: ["CoachDev", "SchoolDev", "Other"],
      cycle_status: ["draft", "active", "locked", "archived"],
      fellows_dev_phasespecialization_enum: [
        "Foundation",
        "Intermediate",
        "Senior",
        "FET",
      ],
      fellows_dev_qualificationtype_enum: ["BEd", "PGCE"],
    },
  },
} as const
