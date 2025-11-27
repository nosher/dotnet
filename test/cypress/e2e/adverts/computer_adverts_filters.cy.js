/// <reference types="cypress" />

describe('nosher.net computer adverts - by filters', () => {


  it('Company links in advert work as expected', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/altair_popelec_aug75')
    // test when company goes to multiple adverts
    cy.get('div.liner').find('a[data-link="Processor_Technology"').eq(0).should('contain.text', 'Processor Technology').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/?type=source&value=Processor')
    })
    cy.visit('http://10.1.203.1:8010/archives/computers/altair_popelec_aug75')
    // test when company goes to single advert
    cy.get('div.liner').find('a[data-link="Polymorphic"').eq(0).should('contain.text', 'Polymorphic').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/polymorphic88_byte_jul77')
    })
  })

  
  it('Adverts by Models contains Sort by Model link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    cy.get('section.archives').find('a[data-id="sorted"').should('contain.text', 'sorted by model name').then(($link) => {
        const href = $link.prop('href')
        cy.visit(href)
        cy.url().should('contain', '/archives/computers/models/sorted')
      })
    }
  )


  it('Adverts by Models sorted contains internal jump links', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/sorted')
    cy.get('section.archives').find('p.jump').find('a').should('have.length', 27) // a-z plus '0-9'
    }
  )


  it('Adverts by Models sorted contains enough groups', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/sorted')
    cy.get('section.archives').find('div.sortmods').should('have.length', 27) // a-z plus '0-9'
    }
  )


  it('Adverts by Models sorted first group contains enough links', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/sorted')
    cy.get('section.archives').find('div.sortmods').eq(0).should(($group) => {
        if ($group.find('a').length < 10) {
          throw new Error('Did not find enough links to models')
        }
      })
    }
  )


  it('Adverts by Models jump link contains correct title', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/sorted')
    cy.get('section.archives').find('a[name="Z"').next().should('contain.text', 'Z')
    }
  )


  it('Adverts by Models sorted first group first link goes to valid page', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/sorted')
    cy.get('section.archives').find('div.sortmods').eq(0).find('a').then(($link) => {
        const href = $link.prop('href')
        cy.visit(href)
        cy.url().should('contain', '/archives/computers/tandy_1000ex_praccomp_apr87')
      })
    }
  )


  it('Adverts by Models title is correct for multiple companies', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/Apple%20Clones')
    cy.get('main#cmain').find('h1').eq(0).should('contain.text', 'Adverts featuring Apple Clones')
  })
  

  it('Adverts by Models title is correct when model also contains company name', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/ACT|Apricot%20Portable')
    cy.get('main#cmain').find('h1').eq(0).should('contain.text', 'Adverts featuring the ACT/Apricot Portable')
  })


  it('Adverts by Models title is correct when model does not contain company name', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/CPC%20464')
    cy.get('main#cmain').find('h1').eq(0).should('contain.text', 'Adverts featuring the Amstrad CPC 464')
  })


  it('Adverts by Models title is correct when model is not a definite article', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/MS-DOS')
    // e.g. should not say 'featuring the MS-DOS'
    cy.get('main#cmain').find('h1').eq(0).should('contain.text', 'Adverts featuring MS-DOS')
  })


  it('Adverts by Models link is present', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/')
    cy.get('p.nav').find('a').eq(5).should('contain.text', 'by model')
  })
  

  it('Adverts by Models has 27 jump-to links ', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    // 26 A-Z links plus one for view-by-sorted
    cy.get('section.archives').find('p').eq(1).find('a').should('have.length', 27)
  })
  

  it('Adverts by Models has 26 jump-to targets ', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    cy.get('section.archives').find('a[name]').should('have.length', 26)
  })


  it('Adverts by Models check Acorn first advert goes straight to page', () => {
    // a single-advert model result should link straight to the target page
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    cy.get('div.models').find('div').eq(0).find('a').contains('Archimedes').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/acorn_archie_percw_jan88')
    })
  })


  it('Adverts by Models check Acorn BBC Micro link goes to thumbnails page', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    cy.get('div.models').find('div').eq(0).find('a').contains('BBC Micro (Proton)').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/model/BBC%20Micro%20(Proton)')
    })
  })


  it('Adverts by Models check model with / does not break', () => {
    // a single-advert model result should link straight to the target page
    cy.visit('http://10.1.203.1:8010/archives/computers/models/')
    cy.get('section.archives').find('div.models').eq(3).find('a').contains('DB 8/1').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/model/DB%208%7C1')
    })
  })

  
  it('Adverts by Models check Atari 520ST page has three links', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/520ST')
    cy.get('div#yearindex').find('div').should('have.length', 3)
  })


  it('Adverts by Models check Atari 520ST page first link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/520ST')
    cy.get('div#yearindex').find('div').eq(0).find('a').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/your_computer_1985-12_001')
    })
  })
  

  it('Adverts by Models check Atari 520ST page first link thumbnail', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/520ST')
    cy.get('div#yearindex').find('div').eq(0).find('img').invoke('attr', 'src')
        .should('contain', '/archives/computers/images/your_computer_1985-12_001-s.webp')
  })


    it('Missing or invalid model lands on 404 page', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/xyz')
    cy.get('section.advert').find('h1.logo').eq(0).should('contain.text', 'Missing Content')
  })


  it('Adverts by Model with text intro', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/testintro')
    cy.get('section.archives').find('div.intro').should('have.length', 1).should('contain.text', "introduction")
  })


  it('Adverts by Model with no text intro', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/model/test')
    cy.get('section.archives').find('div.intro').should('have.length', 0)
  })


  it('By CPU link is present', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/?type=year&value=1980')
    cy.get('p.nav').find('a').eq(6).should('contain.text', 'by CPU')
  })


  it('Adverts by CPU', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/')
    cy.get('section.archives').find('h3').first().should('contain.text', '8-bit CPUs')
  })


  it('Adverts by CPU - first 8-bit link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/')
    cy.get('section.archives').find('li').first().find('a').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/cpus/Capricorn')
      cy.get('main#cmain').find('h1').first().should('contain.text', "3 adverts that feature the Hewlett-Packard Capricorn")
    })
  })


  it('Adverts by CPU - single-advert 8-bit link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/LH5801')
    cy.url().should('contain', '/archives/computers/sharp_pc1500_perscomp_may82')
  })


  it('Adverts by CPU - first 8-bit link text is correct', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/')
    cy.get('section.archives').find('li').first().find('p').first().should('contain.text', '16 bit address (64K memory max), proprietary HP CPU')
  })


  it('Adverts by CPU - check thumbnail image is present', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/Capricorn')
    cy.get('section.archives').find('a').first().find('img').should('have.length', 1).should('have.prop', 'src')
      .and('include', 'hp85_pcw_nov80-s.webp')
  })


  it('Adverts by CPU - check 70+ thumbnail images are present for 6502', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/6502')
    cy.get('section.archives').find('div#yearindex').find('img').should(($images) => {
      if ($images.length < 50 ) {
        throw new Error('Not enough thumbnails')
      }
    })
  })


  it('Adverts by CPU - visit the first 8-bit link', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/Capricorn')
    cy.get('section.archives').find('a').first().then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/hp85_pcw_nov80')
    })
  })


    it('Missing or invalid CPU lands on 404 page', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/cpus/xyz')
    cy.get('section.advert').find('h1.logo').eq(0).should('contain.text', 'Missing Content')
  })


  it('CPU links in advert work as expected', () => {
    cy.visit('http://10.1.203.1:8010/archives/computers/altair_popelec_aug75')
    // test when CPU and text are the same
    cy.get('div.liner').find('a[data-link="8080"').eq(0).should('contain.text', '8080').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/cpus/8080')
    })

    //test when CPU and text are different
    cy.visit('http://10.1.203.1:8010/archives/computers/altair_popelec_aug75')
    cy.get('div.liner').find('a[data-link="Z80"').eq(0).should('contain.text', 'Zilog Z80').then(($link) => {
      const href = $link.prop('href')
      cy.visit(href)
      cy.url().should('contain', '/archives/computers/cpus/Z80')
    })
  })

  
})
