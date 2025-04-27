import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

// Lucide setup
import { LucideAngularModule } from 'lucide-angular';
import { Home, User, Book, FileText, 
  Settings, PlusCircle, BookMarked, ClockArrowDown, Clock, Plus } from 'lucide-angular';


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
      Plus
    }),    
  ],
  exports: [
    LucideAngularModule,
    
  ]
})
export class IconModule {}
