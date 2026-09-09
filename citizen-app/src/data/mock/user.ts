import { UserProfile } from '../../types';

export const mockUserProfile: UserProfile = {
  name: 'Priya Sharma',
  phone: '+91 98765 43210',
  bloodGroup: 'O+ Positive',
  location: 'Brodipet, Guntur, Andhra Pradesh',
  householdMembers: 3,
  specialNeeds: ['Elderly resident (age 74, mobility assistance)'],
  emergencyContacts: [
    {
      name: 'Dr. Rajesh Sharma',
      relation: 'Spouse',
      phone: '+91 98765 11223',
    },
    {
      name: 'Ananya Sharma',
      relation: 'Daughter',
      phone: '+91 98765 99887',
    },
    {
      name: 'District Disaster Control Room',
      relation: 'Emergency Helpline',
      phone: '1077',
    },
  ],
  checklistCompleted: 5,
  checklistTotal: 7,
};
