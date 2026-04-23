import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

// Lucide setup
import { LucideAngularModule } from 'lucide-angular';
import {
  Award,
  Book,
  BookMarked,
  BookOpen,
  ClipboardList,
  Clock,
  ClockArrowDown,
  FileText,
  Home,
  Mail,
  Plus,
  PlusCircle,
  Settings,
  SlidersHorizontal,
  User,
  Users,
} from 'lucide-angular';


@NgModule({
  imports: [
    CommonModule,
    LucideAngularModule.pick({
      Home,
      User,
      Book,
      FileText,
      Settings,
      PlusCircle,
      BookMarked,
      ClockArrowDown,
      Clock,
      Plus,
      Award,
      ClipboardList,
      Mail,
      BookOpen,
      Users,
      SlidersHorizontal,
    }),    
  ],
  exports: [
    LucideAngularModule,
    
  ]
})
export class IconModule {}
